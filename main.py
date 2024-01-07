import subprocess
import urllib.parse
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

class TerminalHandler(BaseHTTPRequestHandler):
    output_buffer = []
    current_directory = os.getcwd()
    command_history = []
    command_index = 0

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()

        command = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('cmd', [''])[0]

        if command:
            command_lower = command.lower()
            if command_lower in ('exit', 'terminate', 'quit', 'close'):
                self.send_exit_response()
            elif command_lower == 'developer':
                self.output_buffer.append(("developer", '<b>Developer:</b> Prince Kakkad</br><a href = "https://codeestro.com/">https://codeestro.com/</a>'))
            elif command_lower in ('clear', 'cls'):
                self.output_buffer.clear()
            elif command_lower.startswith('cd '):
                self.change_directory(command_lower[3:])
            elif command_lower == 'ls':
                self.run_ls_command()
            else:
                self.command_history.append(command)
                self.command_index = len(self.command_history)
                result = self.run_command(command)
                self.output_buffer.append((command, result))

        self.wfile.write(self.generate_page().encode('utf-8'))

    def send_exit_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        page_content = """
        <html>
        <head>
            <title>Web Linux Terminal - Goodbye</title>
            <meta http-equiv="refresh" content="10;url=https://codeestro.com/">
            <style>
            #countdown {
                font-weight: bold;
                font-size: 2em;
            }
            </style>

                
            <script>
                var countdown = 10;
                function updateCountdown() {
                    countdown--;
                    document.getElementById("countdown").innerText = countdown;
                    if (countdown <= 0) {
                        window.location.href = "https://codeestro.com/";
                    } else {
                        setTimeout(updateCountdown, 1100);
                    }
                }
                document.addEventListener("DOMContentLoaded", function() {
                    updateCountdown();
                });
            </script>
        </head>
        <body>
            <h1>Goodbye!</h1>
            <p>Thank you for using the Web Linux Terminal.</p>
            <p>You will be redirected to <a href="https://codeestro.com/">https://codeestro.com/</a> in <b><span id="countdown">10</span> seconds.</b></p>
        </body>
        </html>
        """
        self.wfile.write(page_content.encode('utf-8'))

    def change_directory(self, directory):
        try:
            new_directory = os.path.join(self.current_directory, directory)
            os.path.normpath(new_directory)
            self.current_directory = new_directory
        except OSError as e:
            self.output_buffer.append(("cd " + directory, str(e)))

    def run_ls_command(self):
        try:
            result = "\n".join(os.listdir(self.current_directory))
            self.output_buffer.append(("ls", result))
        except OSError as e:
            self.output_buffer.append(("ls", str(e)))

    def generate_page(self):
        page_content = """
        <html>
        <head>
            <title>Web Linux Terminal</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: black;
                    color: green;
                    font-family: 'Ubuntu';
                    font-style: normal;
                    font-size: 1.2em;
                }
                #terminal {
                    white-space: pre-wrap;
                }
                #input-container {
                    display: flex;
                    align-items: baseline;
                    background: transparent;
                    border: none;
                    outline: none;
                    width: 100%;
                }
                #prompt {
                    font-weight: bold;
                }
                #input {
                    background: transparent;
                    border: 0;
                    font-size: 1.2em;
                    color: green;
                    focus: none;
                    width: 100%;
                }
                input[type="submit"] {
                    display: none;
                    background-color: green;
                    color: black;
                    border: 0;
                    padding: 2px 6px;
                    cursor: pointer;
                }
                #directory {
                    color: darkblue;
                }
            </style>
        </head>
        <body>
        <h1>Web Linux Terminal</h1>
        <p>Developer: Prince Kakkad</p>
        <p>Copy Rights: <a href="https://codeestro.com/">codeestro.com</a></p>

            <div id="terminal">
        """

        for cmd, output in self.output_buffer:
            page_content += f"<p>root@<span id = 'directory'>{self.current_directory}</span>:~$ {cmd}</p>"
            page_content += f"<pre>{output}</pre>"

        page_content += """
            </div>
            <div id="input-container">
                <span id="prompt">"""
        page_content += f"root@<span id = 'directory'>{self.current_directory}</span>:~$"
        page_content +="""</span>
                <form method="get">
                    <input id="input" type="text" name="cmd" autofocus onkeydown="handleKeyDown(event)" autocomplete="off">
                    <input type="submit">
                </form>
            </div>
            <script>
            """
        
        page_content += """
                var commandHistory = """
        page_content += str(self.command_history)  # Convert list to string
        page_content += ";"
        
        page_content += """
                var commandIndex = """
        page_content += str(self.command_index)  # Convert integer to string
        page_content += ";"
        
        page_content += """
                function handleKeyDown(event) {
                    if (event.key === "ArrowUp" && commandIndex > 0) {
                        commandIndex--;
                        document.getElementById("input").value = commandHistory[commandIndex];
                        event.preventDefault();
                    } else if (event.key === "ArrowDown" && commandIndex < commandHistory.length - 1) {
                        commandIndex++;
                        document.getElementById("input").value = commandHistory[commandIndex];
                        event.preventDefault();
                    }
                }
            </script>
        </body>
        </html>
        """

        return page_content

    def run_command(self, command):
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            result = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                result.append(line)
            return '\n'.join(result)
        except subprocess.CalledProcessError as e:
            return str(e.output)

def run(server_class=HTTPServer, handler_class=TerminalHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Web Linux Terminal")
    print(f"Starting server on port {port}...")
    print(f"Open http://localhost:{port} in your browser to access the terminal")
    print(f"Developed by: Prince Kakkad")
    print(f"Copy Right: https://codeestro.com/")
    webbrowser.open_new(f'http://localhost:{port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
