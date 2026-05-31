import os

def shred_file(file_path, passes=3):
    """Securely overwrite a file before deletion to prevent recovery."""
    if not os.path.exists(file_path):
        return False
    
    try:
        length = os.path.getsize(file_path)
        with open(file_path, "ba+") as f:
            for _ in range(passes):
                f.seek(0)
                # Overwrite with random bytes
                f.write(os.urandom(length))
                # Ensure it's written to disk
                f.flush()
                os.fsync(f.fileno())
        
        # After securely overwriting the data, delete the file handle
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Failed to shred file: {e}")
        return False
