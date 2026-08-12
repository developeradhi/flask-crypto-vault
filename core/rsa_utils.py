import rsa
import base64

def generate_rsa_keypair():
    """Generates a new RSA 2048-bit key pair."""
    pub_key, priv_key = rsa.newkeys(2048)
    pub_pem = pub_key.save_pkcs1().decode('utf-8')
    priv_pem = priv_key.save_pkcs1().decode('utf-8')
    return pub_pem, priv_pem

def sign_message(private_key_pem, message):
    """Signs a message using the user's private RSA key."""
    try:
        priv_key = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
        signature = rsa.sign(message.encode('utf-8'), priv_key, 'SHA-256')
        return True, base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        return False, str(e)

def verify_signature(public_key_pem, message, signature_b64):
    """Verifies a signature using the public RSA key."""
    try:
        pub_key = rsa.PublicKey.load_pkcs1(public_key_pem.encode('utf-8'))
        signature = base64.b64decode(signature_b64)
        # Returns the hash algorithm name if valid, else raises VerificationError
        rsa.verify(message.encode('utf-8'), signature, pub_key)
        return True, "Signature is valid and authentic."
    except rsa.VerificationError:
        return False, "Signature is INVALID or message was tampered with."
    except Exception as e:
        return False, str(e)
