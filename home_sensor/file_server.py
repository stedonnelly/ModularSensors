import uzlib
import uio
import socket
import os
import uasyncio as asyncio

# Asynchronous function to extract files from a ZIP archive
async def extract_zip(zip_path, target_path):
    with open(zip_path, 'rb') as f:
        stream = f.read()
        decompressor = uzlib.DecompIO(uio.BytesIO(stream), -15)  # -15 for raw deflate
        zipfile = uio.BytesIO(decompressor.read())
        # Assumes the zip contains a single compressed file
        # For a more complex structure, you would need to parse the zip file properly
        with open(target_path, 'wb') as out_file:
            out_file.write(zipfile.read())

# Asynchronous file server method to handle ZIP uploads
async def start_file_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('File server listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)

        request = cl.recv(1024).decode()

        if 'Content-Disposition' in request:
            filename_start = request.find('filename="') + 10
            filename_end = request.find('"', filename_start)
            filename = request[filename_start:filename_end]
            print("Uploading file:", filename)

            if filename.endswith('.zip'):
                # Assume the target path is /flash/
                folder = '/flash/'

                file_start = request.find('\r\n\r\n') + 4
                file_end = request.find('------WebKitFormBoundary', file_start) - 4
                file_data = request[file_start:file_end]

                # Save the ZIP file to flash
                zip_path = f'{folder}{filename}'
                with open(zip_path, 'wb') as f:
                    f.write(file_data.encode())

                # Extract the ZIP file
                await extract_zip(zip_path, folder)

                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h2>ZIP file uploaded and extracted successfully!</h2>'
            else:
                response = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<h2>Only ZIP files are accepted!</h2>'
        else:
            # HTML form for uploading the ZIP file
            html = """
            <!DOCTYPE html>
            <html>
                <body>
                    <h1>Upload a ZIP file to ESP32</h1>
                    <form method="POST" enctype="multipart/form-data">
                        <label>Select ZIP:</label><input type="file" name="file"><br>
                        <input type="submit" value="Upload">
                    </form>
                </body>
            </html>
            """
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html

        cl.send(response)
        cl.close()

# Function to launch the file server asynchronously
async def launch_file_server():
    print("Starting file server...")
    await start_file_server()
