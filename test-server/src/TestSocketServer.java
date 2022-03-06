import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.atomic.AtomicInteger;

public class TestSocketServer
{
    private ServerSocket serverSocket;
    private static AtomicInteger counter = new AtomicInteger(0);

    public static void main(String[] args) throws Exception {
        TestSocketServer server = new TestSocketServer();
        server.start(10500);
    }

    public void start(int port) throws Exception {
        serverSocket = new ServerSocket(port);
        System.out.println("Started on port: " + port);
        while (true)
            new SocketHandler(serverSocket.accept()).start();
    }

    public void stop() throws Exception {
        serverSocket.close();
    }

    private static class SocketHandler extends Thread {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;

        public SocketHandler(Socket socket) {
            this.clientSocket = socket;
        }

        public void run() {
            try {
                int incrementAndGet = counter.incrementAndGet();
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(
                        new InputStreamReader(clientSocket.getInputStream()));

                //String inputLine = in.readLine();

                out.println("closing");

                //System.out.println(inputLine);
                System.out.println("Requests: " + incrementAndGet);

                in.close();
                out.close();
                clientSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
