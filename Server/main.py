import sys
import threading
import signal
import os
import time
from server import Server
from picamera2 import Picamera2

class ServerController:
    def __init__(self):
        self.TCP_Server = Server()
        self.is_running = False
        self.threads = []
        self.stop_event = threading.Event()
        self.picam2 = None
        self.buzzer = self.TCP_Server.buzzer  # 使用 Server 类中的蜂鸣器对象
        self.led = self.TCP_Server.led

    def start_server(self):
        if not self.is_running:
            print("Starting server...")

            # LED闪烁和蜂鸣器声音的启动序列
            self.startup_sequence()

            self.TCP_Server.StartTcpServer()
            self.threads = [
                threading.Thread(target=self.run_thread, args=(self.TCP_Server.readdata, "ReadData")),
                threading.Thread(target=self.run_thread, args=(self.TCP_Server.sendvideo, "SendVideo")),
                threading.Thread(target=self.run_thread, args=(self.TCP_Server.Power, "Power"))
            ]
            for thread in self.threads:
                thread.daemon = True
                thread.start()
            self.is_running = True
            print("Server started")
        else:
            print("Server is already running")
    

    def startup_sequence(self):

        # 同时闪烁LED和发出蜂鸣声
        for _ in range(3):
            self.buzzer.run('1')
            self.led.ledIndex(0xFF, 255, 255, 255)
            time.sleep(0.1)
            self.buzzer.run('0')
            self.led.ledIndex(0xFF, 0, 0, 0)
            time.sleep(0.2)


    def run_thread(self, target, name):
        while not self.stop_event.is_set():
            try:
                target()
            except Exception as e:
                print(f"Error in {name} thread: {e}")
                break

    def stop_server(self):
        if self.is_running:
            print("Stopping server...")
            self.stop_event.set()
            self.TCP_Server.StopTcpServer()
            for thread in self.threads:
                thread.join(timeout=3)  # 给每个线程3秒时间来结束
            self.is_running = False
            print("Server stopped")
        else:
            print("Server is not running")

    def run(self):
        self.start_server()  # 自动开启 TCP 服务器
        
        while True:
            try:
                command = input("Enter command (stop/restart/quit): ").lower()
                if command == 'stop':
                    self.stop_server()
                elif command == 'restart':
                    self.stop_server()
                    self.start_server()
                elif command == 'quit':
                    if self.is_running:
                        self.stop_server()
                    print("Exiting program")
                    break
                else:
                    print("Invalid command. Please use 'stop', 'restart', or 'quit'.")
            except KeyboardInterrupt:
                print("\nProgram interrupted by user")
                break

def cleanup():
    print("Cleaning up resources...")
    try:
        if hasattr(Picamera2, 'global_cleanup'):
            Picamera2.global_cleanup()
        else:
            print("Picamera2 global_cleanup not available")
    except Exception as e:
        print(f"Error during Picamera2 cleanup: {e}")

def force_quit(signum, frame):
    print("\nForce quitting due to timeout")
    cleanup()
    os._exit(1)

if __name__ == '__main__':
    controller = ServerController()
    
    def shutdown(signum, frame):
        print("\nShutdown signal received")
        controller.stop_server()
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        controller.run()
    finally:
        cleanup()
        
        print("Waiting for all threads to finish (10 seconds timeout)...")
        timeout = time.time() + 10
        while threading.active_count() > 1 and time.time() < timeout:
            time.sleep(0.1)
        
        remaining_threads = threading.enumerate()
        if len(remaining_threads) > 1:
            print(f"Force quitting. {len(remaining_threads) - 1} threads did not finish in time:")
            for thread in remaining_threads:
                if thread != threading.current_thread():
                    print(f"- {thread.name}")
            os._exit(1)
        else:
            print("All threads finished. Exiting normally.")
            sys.exit(0)