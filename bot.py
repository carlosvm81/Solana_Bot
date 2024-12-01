import asyncio
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solana.keypair import Keypair
from spl.token.instructions import transfer_checked, get_account_info
from spl.token.constants import TOKEN_PROGRAM_ID
import os

# Configuración inicial
RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"  # Cambia a la red que uses (Mainnet, Devnet, etc.)
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")  # Llave privada de tu billetera en formato JSON

# Clase del bot
class SolanaBot:
    def __init__(self, rpc_endpoint, wallet_private_key):
        self.rpc_endpoint = rpc_endpoint
        self.wallet_keypair = Keypair.from_secret_key(bytes(eval(wallet_private_key)))

    async def get_balance(self):
        """Consulta el saldo de SOL en la cuenta del bot."""
        async with AsyncClient(self.rpc_endpoint) as client:
            balance = await client.get_balance(self.wallet_keypair.pubkey())
            return balance["result"]["value"] / 1e9  # Convierte de lamports a SOL

    async def transfer_tokens(self, destination_pubkey, token_mint, amount):
        """Transfiere tokens SPL a otra cuenta."""
        destination = Pubkey.from_string(destination_pubkey)
        token_mint = Pubkey.from_string(token_mint)
        
        async with AsyncClient(self.rpc_endpoint) as client:
            # Obtén la cuenta asociada al token
            response = await client.get_token_accounts_by_owner(self.wallet_keypair.pubkey(), {"mint": token_mint})
            if not response["result"]["value"]:
                raise ValueError("La billetera no tiene una cuenta asociada para este token.")
            
            source_token_account = Pubkey.from_string(response["result"]["value"][0]["pubkey"])
            
            # Crear y enviar la transacción
            tx = Transaction()
            transfer_instruction = transfer_checked(
                source=source_token_account,
                dest=destination,
                owner=self.wallet_keypair.pubkey(),
                amount=int(amount * 10**6),  # Ajusta los decimales según el token
                decimals=6,  # Decimales del token
                mint=token_mint,
            )
            tx.add(transfer_instruction)
            response = await client.send_transaction(tx, self.wallet_keypair, opts=TxOpts(skip_preflight=True))
            return response

    async def monitor_market(self):
        """Lógica del bot para monitorizar oportunidades."""
        while True:
            # Aquí puedes añadir la lógica personalizada para monitorizar tokens o precios
            print("Monitorizando el mercado...")
            await asyncio.sleep(10)

async def main():
    # Inicializa el bot
    bot = SolanaBot(RPC_ENDPOINT, WALLET_PRIVATE_KEY)

    # Verifica el saldo
    balance = await bot.get_balance()
    print(f"Saldo en SOL: {balance}")

    # Transferencia de prueba (opcional)
    try:
        response = await bot.transfer_tokens(
            destination_pubkey=An1zmvLGEPczUmpbCwriYoJMeMtKLDDBPDAJCbhnzGjV,
            token_mint="MINT_DEL_TOKEN",
            amount=0.01,  # Cantidad del token
        )
        print(f"Transacción completada: {response}")
    except Exception as e:
        print(f"Error en la transferencia: {e}")

    # Inicia la monitorización del mercado
    await bot.monitor_market()

# Ejecuta el bot
if __name__ == "__main__":
    asyncio.run(main())
