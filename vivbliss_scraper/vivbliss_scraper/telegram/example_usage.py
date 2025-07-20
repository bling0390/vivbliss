"""
Example usage of the Telegram file upload functionality.
"""
import asyncio
import os
from .config import TelegramConfig
from .file_validator import FileValidator
from .file_uploader import FileUploader


async def example_upload_workflow():
    """Example of complete file upload workflow."""
    
    # Step 1: Configure Telegram client
    config = TelegramConfig(
        api_id="YOUR_API_ID",
        api_hash="YOUR_API_HASH", 
        session_name="vivbliss_uploader"
    )
    
    # Step 2: Create and start client
    client = await config.create_client()
    await client.start()
    
    try:
        # Step 3: Validate connection
        if not await config.validate_client_connection(client):
            print("Failed to connect to Telegram")
            return
        
        # Step 4: Initialize file validator and uploader
        validator = FileValidator()
        uploader = FileUploader(client)
        
        # Step 5: Example file paths (replace with actual paths)
        example_files = [
            "/path/to/image.jpg",
            "/path/to/video.mp4",
            "/path/to/another_image.png"
        ]
        
        # Step 6: Upload files
        chat_id = -1001234567890  # Replace with your chat ID
        
        for file_path in example_files:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            # Validate file
            validation = validator.validate_file(file_path)
            if not validation['is_valid']:
                print(f"Invalid file {file_path}: {validation['errors']}")
                continue
            
            # Upload file
            result = await uploader.upload_file(
                chat_id=chat_id,
                file_path=file_path,
                caption=f"Uploaded from VivBliss scraper: {os.path.basename(file_path)}"
            )
            
            if result['success']:
                print(f"✅ Uploaded {file_path} - Message ID: {result['message_id']}")
            else:
                print(f"❌ Failed to upload {file_path}: {result['error']}")
        
        # Step 7: Batch upload example
        print("\\n--- Batch Upload Example ---")
        results = await uploader.upload_multiple_files(
            chat_id=chat_id,
            file_paths=example_files,
            progress_callback=lambda current, total, file: print(f"Progress: {current}/{total} - {file}")
        )
        
        successful_uploads = sum(1 for r in results if r['success'])
        print(f"Batch upload completed: {successful_uploads}/{len(results)} successful")
        
    finally:
        # Step 8: Clean up
        await client.stop()


def example_validation_only():
    """Example of file validation without upload."""
    validator = FileValidator()
    
    test_files = [
        "image.jpg",
        "video.mp4", 
        "document.txt",
        "large_file.mov"
    ]
    
    print("File Validation Results:")
    print("-" * 40)
    
    for file_path in test_files:
        result = validator.validate_file(file_path)
        status = "✅ Valid" if result['is_valid'] else "❌ Invalid"
        print(f"{file_path}: {status}")
        
        if not result['is_valid']:
            print(f"  Errors: {', '.join(result['errors'])}")
        
        print(f"  Type: {result['file_type']}")
        print(f"  Extension: {result['extension']}")
        print()


if __name__ == "__main__":
    print("=== Telegram File Upload Example ===\\n")
    
    # Run validation example (works without Telegram credentials)
    example_validation_only()
    
    print("\\n=== Upload Example ===")
    print("To run upload example, set your Telegram credentials and uncomment the line below:")
    print("# asyncio.run(example_upload_workflow())")