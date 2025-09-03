import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import estoque as models, movimentacoes_estoque as mov_models
from ..schemas import estoque as schemas, movimentacoes_estoque as mov_schemas
from ..models.movimentacoes_estoque import TipoMovimentacao
from ..services.notification_service import NotificationService
from ..models.tenant_configs import ConfigKey
from ..core.units import convert_units, get_unit_dimension, get_base_unit_for_dimension

# CRUD for Estoque
async def get_estoque_item(db: AsyncSession, item_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Estoque).filter_by(id=item_id, tenant_id=tenant_id))
    return result.scalars().first()

async def get_estoque_itens(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Estoque).filter_by(tenant_id=tenant_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_estoque_item(db: AsyncSession, item: schemas.EstoqueCreate, tenant_id: uuid.UUID):
    # Check if an item with the same name already exists for this tenant
    existing_item = await db.execute(
        select(models.Estoque).filter_by(nome=item.nome, tenant_id=tenant_id)
    )
    if existing_item.scalars().first():
        raise HTTPException(status_code=409, detail="Item de estoque com este nome já existe para este tenant.")

    db_item = models.Estoque(
        **item.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_estoque_item(db: AsyncSession, item_id: uuid.UUID, item_data: schemas.EstoqueUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Estoque).filter_by(id=item_id, tenant_id=tenant_id))
    db_item = result.scalars().first()
    if db_item:
        update_data = item_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        await db.commit()
        await db.refresh(db_item)
    return db_item

async def delete_estoque_item(db: AsyncSession, item_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Estoque).filter_by(id=item_id, tenant_id=tenant_id))
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
    return db_item

# CRUD for MovimentacoesEstoque
async def create_movimentacao(db: AsyncSession, movimentacao: mov_schemas.MovimentacaoEstoqueCreate, tenant_id: uuid.UUID):
    # Get the item from stock
    item_result = await db.execute(select(models.Estoque).filter_by(id=movimentacao.produto_id, tenant_id=tenant_id))
    db_item = item_result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")

    # Get tenant and paciente names for PDF path
    tenant_result = await db.execute(select(tenant_models.Tenant).filter_by(id=tenant_id))
    tenant = tenant_result.scalars().first()
    paciente_result = await db.execute(select(paciente_models.Paciente).filter_by(id=movimentacao.paciente_id))
    paciente = paciente_result.scalars().first()

    converted_quantidade = Decimal(str(movimentacao.quantidade))

    # Check for sufficient stock on 'saida'
    if movimentacao.tipo == TipoMovimentacao.saida and db_item.quantidade < converted_quantidade:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque.")

    # Create the movement record
    db_movimentacao = mov_models.MovimentacaoEstoque(
        **movimentacao.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_movimentacao)

    # Update the stock quantity
    if movimentacao.tipo == TipoMovimentacao.entrada:
        db_item.quantidade += converted_quantidade
    else: # saida
        db_item.quantidade -= converted_quantidade
    
    await db.commit()
    await db.refresh(db_movimentacao)

    # Generate PDF
    if tenant and paciente:
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprovante de Retirada de Material</title>
            <style>
                body { font-family: sans-serif; }
                h1 { text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Comprovante de Retirada de Material</h1>
            <p><strong>Clínica:</strong> {{ tenant_name }}</p>
            <p><strong>Paciente:</strong> {{ paciente_name }}</p>
            <p><strong>Data:</strong> {{ data }}</p>
            <table>
                <tr>
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Observação</th>
                </tr>
                <tr>
                    <td>{{ produto_nome }}</td>
                    <td>{{ quantidade }} {{ unidade }}</td>
                    <td>{{ observacao }}</td>
                </tr>
            </table>
        </body>
        </html>
        """
        template = jinja2.Template(template_str)
        html_content = template.render(
            tenant_name=tenant.nome,
            paciente_name=paciente.nome,
            data=db_movimentacao.data.strftime("%d/%m/%Y %H:%M:%S"),
            produto_nome=db_item.nome,
            quantidade=db_movimentacao.quantidade,
            unidade=db_item.unidade,
            observacao=db_movimentacao.observacao or ''
        )

        pdf_path = os.path.join("storage", tenant.nome, "prontuario")
        os.makedirs(pdf_path, exist_ok=True)
        pdf_file = os.path.join(pdf_path, f"comprovante_{db_movimentacao.id}.pdf")
        with open(pdf_file, "wb") as f:
            pisa.CreatePDF(html_content, dest=f)

    # Check for low stock and send alert
    if db_item.quantidade <= db_item.min_quantidade:
        notification_service = NotificationService(db)
        # For now, assume a fixed recipient or fetch from tenant_configs if a specific key is defined for manager email
        # For simplicity, let's assume a config key for manager email exists or use a placeholder
        manager_email = await notification_service._get_tenant_config(tenant_id, ConfigKey.smtp_user) # Using smtp_user as a placeholder for manager email
        if manager_email:
            subject = f"Alerta de Estoque Baixo: {db_item.nome}"
            body = f"""Prezado(a) Gestor(a),

O item '{db_item.nome}' atingiu um nível de estoque baixo.
Quantidade atual: {db_item.quantidade} {db_item.unidade}.
Quantidade mínima: {db_item.min_quantidade} {db_item.unidade}.

Por favor, providencie a reposição.

Atenciosamente,
Sistema de Gestão de Clínicas"""
            await notification_service.send_email(tenant_id, manager_email, subject, body)
        else:
            print(f"WARNING: Estoque baixo para {db_item.nome}, mas e-mail do gestor não configurado para o tenant {tenant_id}.")

    return db_movimentacao

async def get_movimentacoes_for_item(db: AsyncSession, produto_id: uuid.UUID, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(mov_models.MovimentacaoEstoque)
        .filter_by(produto_id=produto_id, tenant_id=tenant_id)
        .order_by(mov_models.MovimentacaoEstoque.data.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_movimentacoes_for_paciente(db: AsyncSession, paciente_id: uuid.UUID, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(mov_models.MovimentacaoEstoque)
        .filter_by(paciente_id=paciente_id, tenant_id=tenant_id)
        .order_by(mov_models.MovimentacaoEstoque.data.desc())
        .options(selectinload(mov_models.MovimentacaoEstoque.produto))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()