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
    private static boolean outEachThousand = false;

    public static void main(String[] args) throws Exception
    {
        String portEnv = System.getenv("PORT");
        int defaultPort = 10500;
        try {
            defaultPort = Integer.parseInt(args[0]);
        }
        catch (Exception ignored) {
        }
        if (null != args) {
            for (String arg : args) {
                if ("mod".equals(arg)) {
                    outEachThousand = true;
                    System.out.println("Will print each thousand request");
                    break;
                }
            }
        }
        TestSocketServer server = new TestSocketServer();
        server.start(portEnv != null && portEnv.length() > 0 ? Integer.parseInt(portEnv) : defaultPort);
    }

    public void start(int port) throws Exception
    {
        serverSocket = new ServerSocket(port);
        System.out.println("Started on port: " + port);
        while (true)
            new SocketHandler(serverSocket.accept()).start();
    }

    public void stop() throws Exception
    {
        serverSocket.close();
    }

    private static class SocketHandler extends Thread
    {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;

        public SocketHandler(Socket socket)
        {
            this.clientSocket = socket;
        }

        public void run()
        {
            try {
                int incrementAndGet = counter.incrementAndGet();
                out = new PrintWriter(clientSocket.getOutputStream(), true);
                in = new BufferedReader(
                        new InputStreamReader(clientSocket.getInputStream()));

                //String inputLine = in.readLine();

                out.println("requests: " + incrementAndGet);

                //System.out.println(inputLine);
                if (outEachThousand) {
                    if (incrementAndGet % 1000 == 0) {
                        System.out.println("Requests: " + incrementAndGet);
                    }
                }
                else {
                    System.out.println("Requests: " + incrementAndGet);
                }

                in.close();
                out.close();
                clientSocket.close();
            }
            catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
