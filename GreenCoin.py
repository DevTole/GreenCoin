from xian_py import Xian, Wallet

# Generate local key pair
new_wallet = Wallet()
private_key = new_wallet.private_key
public_key = new_wallet.public_key

# Define node endpoint
node_url = "https://testnet.xian.org"

# Initialize connection
# This binds the generated keys to the network interface
xian = Xian(node_url, wallet=new_wallet)

# Verify connection status
try:
    node_status = xian.get_status()
    print(f"Public Key: {public_key}")
    print(f"Private Key: {private_key}")
    print(f"Status: Connected to {node_url}")
except Exception as e:
    print(f"Connection Failed: {e}")
