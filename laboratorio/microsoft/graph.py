import asyncio
import os 
from dotenv import load_dotenv
from azure.identity.aio import ClientSecretCredential
from typing import cast
import pdb

load_dotenv()

class Graph:
    """
    Clase para la verificación de MicrosoftGraph
    """
    def __init__(self) -> None:
        self.TENANTID       = cast(str, os.getenv("TENANT"))
        self.CLIENTID       = cast(str, os.getenv("APPLICATION_ID"))
        self.CLIENTSECRET   = cast(str, os.getenv("SECRET_VALUE"))
        print(f"Variables de entorno - TENANTID: {self.TENANTID}, CLIENTID: {self.CLIENTID}, CLIENTSECRET: {'***' if self.CLIENTSECRET else None}")

        if not all([self.TENANTID,self.CLIENTID,self.CLIENTSECRET]):
            raise ValueError("Faltan las variables de entorno")
        
        self.credential = ClientSecretCredential(self.TENANTID,self.CLIENTID,self.CLIENTSECRET)

    
    async def get_token(self):
        """
        Obtiene el Token que será utilizado en las solicitudes de microsoft
        """
        scopes = ['https://graph.microsoft.com/.default']
        print(f"Scopes usados: {scopes}")
        token = await self.credential.get_token(*scopes)
        if not token:
            print(f"Token: {token}")
        print(f"Token obtenido: {token.token[:10]}... (truncado por seguridad)")
        return token.token