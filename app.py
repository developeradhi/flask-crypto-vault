import argparse
import sys
from core.crypto import generate_key, encrypt_file, decrypt_file
from core.batch import process_directory

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("="*50)
    print("  SECURE FILE ENCRYPTOR & DECRYPTOR (CLI)")
    print("="*50)
    print(f"{Colors.ENDC}")

def handle_generate_key(args):
    print(f"{Colors.OKBLUE}[*] Generating new encryption key...{Colors.ENDC}")
    success, msg = generate_key()
    if success:
        print(f"{Colors.OKGREEN}[+] {msg}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}[!] {msg}{Colors.ENDC}")

def handle_encrypt(args):
    if not args.file and not args.dir:
        print(f"{Colors.FAIL}[-] Error: You must specify either --file or --dir for encryption.{Colors.ENDC}")
        sys.exit(1)
        
    if args.file:
        print(f"{Colors.OKBLUE}[*] Encrypting file: {args.file}{Colors.ENDC}")
        success, msg = encrypt_file(args.file)
        if success:
            print(f"{Colors.OKGREEN}[+] {msg}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[-] {msg}{Colors.ENDC}")
            
    if args.dir:
        print(f"{Colors.OKBLUE}[*] Encrypting directory: {args.dir}{Colors.ENDC}")
        success, results = process_directory(args.dir, action="encrypt")
        if not success:
            print(f"{Colors.FAIL}[-] Error: {results}{Colors.ENDC}")
        else:
            print(f"\n{Colors.BOLD}Batch Processing Results:{Colors.ENDC}")
            for detail in results["details"]:
                if detail.startswith("[SUCCESS]"):
                    print(f"  {Colors.OKGREEN}{detail}{Colors.ENDC}")
                elif detail.startswith("[SKIPPED]"):
                    print(f"  {Colors.WARNING}{detail}{Colors.ENDC}")
                else:
                    print(f"  {Colors.FAIL}{detail}{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Summary: {results['success']} encrypted, {results['skipped']} skipped, {results['failed']} failed.{Colors.ENDC}")


def handle_decrypt(args):
    if not args.file and not args.dir:
        print(f"{Colors.FAIL}[-] Error: You must specify either --file or --dir for decryption.{Colors.ENDC}")
        sys.exit(1)
        
    if args.file:
        print(f"{Colors.OKBLUE}[*] Decrypting file: {args.file}{Colors.ENDC}")
        success, msg = decrypt_file(args.file)
        if success:
            print(f"{Colors.OKGREEN}[+] {msg}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[-] {msg}{Colors.ENDC}")
            
    if args.dir:
        print(f"{Colors.OKBLUE}[*] Decrypting directory: {args.dir}{Colors.ENDC}")
        success, results = process_directory(args.dir, action="decrypt")
        if not success:
            print(f"{Colors.FAIL}[-] Error: {results}{Colors.ENDC}")
        else:
            print(f"\n{Colors.BOLD}Batch Processing Results:{Colors.ENDC}")
            for detail in results["details"]:
                if detail.startswith("[SUCCESS]"):
                    print(f"  {Colors.OKGREEN}{detail}{Colors.ENDC}")
                elif detail.startswith("[SKIPPED]"):
                    print(f"  {Colors.WARNING}{detail}{Colors.ENDC}")
                else:
                    print(f"  {Colors.FAIL}{detail}{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Summary: {results['success']} decrypted, {results['skipped']} skipped, {results['failed']} failed.{Colors.ENDC}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Secure CLI File Encryptor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate Key Command
    parser_keygen = subparsers.add_parser("generate-key", help="Generate a new encryption key")
    
    # Encrypt Command
    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt a file or directory")
    parser_encrypt.add_argument("--file", "-f", type=str, help="Path to the file to encrypt")
    parser_encrypt.add_argument("--dir", "-d", type=str, help="Path to the directory to encrypt")
    
    # Decrypt Command
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt a file or directory")
    parser_decrypt.add_argument("--file", "-f", type=str, help="Path to the file to decrypt")
    parser_decrypt.add_argument("--dir", "-d", type=str, help="Path to the directory to decrypt")
    
    args = parser.parse_args()
    
    if args.command == "generate-key":
        handle_generate_key(args)
    elif args.command == "encrypt":
        handle_encrypt(args)
    elif args.command == "decrypt":
        handle_decrypt(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
