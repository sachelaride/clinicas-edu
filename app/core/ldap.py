import os
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from dotenv import load_dotenv

load_dotenv()

LDAP_SERVER_URI = os.getenv("LDAP_SERVER_URI")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN")

def authenticate_ldap_user(username, password):
    if not LDAP_SERVER_URI:
        return None

    try:
        server = Server(LDAP_SERVER_URI, get_info=ALL)
        conn = Connection(server, user=username, password=password, authentication=NTLM, auto_bind=True)
        
        if conn.bound:
            # search_filter = f'(sAMAccountName={username.split("\\")[-1]})' # for Active Directory
            search_filter = f'(uid={username})' # for OpenLDAP
            conn.search(LDAP_BASE_DN, search_filter, attributes=['cn', 'displayName'])
            
            if conn.entries:
                user_entry = conn.entries[0]
                user_info = {
                    "username": username,
                    "dn": user_entry.entry_dn,
                    "cn": user_entry.cn.value if 'cn' in user_entry else user_entry.displayName.value
                }
                conn.unbind()
                return user_info
            else:
                conn.unbind()
                return None # User authenticated but not found in search

    except Exception as e:
        print(f"LDAP Authentication failed: {e}")
        return None
    
    return None
