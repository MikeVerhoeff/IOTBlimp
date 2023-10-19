import com.fazecast.jSerialComm.SerialPort;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.image.ImageView;
import javafx.scene.layout.VBox;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

public class Controller {

    @FXML
    private TextArea pythonOutputTextField;

    @FXML
    private TextField scriptDirectoryField;

    @FXML
    private TextField dataDirField;

    @FXML
    private TextField experimentNameField;

    @FXML
    private VBox imagesBox;

    @FXML
    private TextField pythonField;

    @FXML
    private TextArea serialOutputTextField;

    @FXML
    private ChoiceBox<Pair<SerialPort, String>> deviceSelector;

    private SerialPort port;
    private OutputStream log;
    private String logFileName;
    int baudRate = 9600;

    @FXML
    public void initialize() {
        scanForDevices();
        pythonField.setText("python");
        dataDirField.setText("data");
        scriptDirectoryField.setText("scripts");
    }

    void scanForDevices() {
        deviceSelector.getItems().clear();
        SerialPort[] ports = SerialPort.getCommPorts();
        for(SerialPort port : ports) {
            System.out.println(port.getPortDescription() + "(" + port.getSystemPortName() + ")");
            deviceSelector.getItems().add(new Pair<>(port, port.getPortDescription() + "(" + port.getSystemPortName() + ")"));
        }
    }

    @FXML
    void scanForDevicesAction(ActionEvent event) {
        scanForDevices();
    }

    @FXML
    void connectAction(ActionEvent event) {
        Pair<SerialPort, String> dev = deviceSelector.getValue();
        if (dev == null) {
            return;
        }
        if(port != null) {
            System.out.println("Closed Old Connection");
            port.closePort();
        }
        System.out.println("Connect to: "+dev.value);
        port = dev.key;
        port.setBaudRate(baudRate);
        port.addDataListener(new SerialListener(e->{
            byte[] newData = new byte[port.bytesAvailable()];
            int numRead = port.readBytes(newData, newData.length);
            //System.out.println("Read " + numRead + " bytes.");
            Platform.runLater(()->{
                serialOutputTextField.appendText(new String(newData, StandardCharsets.UTF_8));
            });
            boolean end_found = false;
            int end_index = 0;
            for (int i=0; i<numRead; i++) {
                if(newData[i]=='e') {
                    System.out.println("End Found");
                    end_found = true;
                    end_index = i;
                }
            }
            if(log != null) {
                try {
                    if (end_found) {
                        log.write(newData, 0, end_index);
                        log.close();
                        log = null;
                        runPythonScripts();
                        System.out.println("Save via end");
                    } else {
                        log.write(newData);
                    }
                } catch (Exception ex) {

                }
            }
        }));
        port.openPort();
    }

    boolean deleteDirectory(File directoryToBeDeleted) {
        File[] allContents = directoryToBeDeleted.listFiles();
        if (allContents != null) {
            for (File file : allContents) {
                deleteDirectory(file);
            }
        }
        return directoryToBeDeleted.delete();
    }
    void runPythonScripts() {
        File scriptDir = new File(scriptDirectoryField.getText());
        scriptDir.mkdir();
        File scriptRunDirectory = new File("tmp");
        if(scriptRunDirectory.exists()) {
            deleteDirectory(scriptRunDirectory);
        }
        scriptRunDirectory.mkdir();
        List<Process> processes = new ArrayList<>(10);
        for(File scriptFile : scriptDir.listFiles()) {
            try {
                System.out.println("Running script: "+scriptFile.getName());
                ProcessBuilder processBuilder = new ProcessBuilder(pythonField.getText(), scriptFile.getAbsolutePath(), logFileName);
                processBuilder.redirectErrorStream(true);

                processBuilder.directory(scriptRunDirectory);

                Process process = processBuilder.start();

                new Thread(()->{
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    reader.lines().<Runnable>map(line -> () -> {
                        pythonOutputTextField.appendText(line);
                        pythonOutputTextField.appendText("\n");
                    }).forEach(Platform::runLater);
                }).start();

                processes.add(process);


            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        for(Process process : processes) {
            try {
                System.out.println("1 Script Done");
                int exitCode = process.waitFor();
                process.destroy();
            } catch (Exception e) {
                e.printStackTrace();
            }
            System.out.println("All scripts Done");
        }
        File finalLocation;
        if (scriptRunDirectory.exists() && !experimentNameField.getText().equals("")) {
            File moveTo = new File(new File(dataDirField.getText()), experimentNameField.getText());
            scriptRunDirectory.renameTo(moveTo);
            finalLocation = moveTo;
        } else {
            finalLocation = scriptRunDirectory;
        }
        Platform.runLater(() -> {
            //System.out.println(finalLocation.getAbsolutePath());
            for(File file : finalLocation.listFiles()) {
                System.out.println(file.getAbsolutePath());
                ImageView imageView = new ImageView(file.getAbsolutePath());
                if(!imageView.getImage().errorProperty().get()) {
                    imagesBox.getChildren().add(imageView);
                }
            }
        });
    }

    void prepareForNewSerialInput() {
        pythonOutputTextField.clear();
        serialOutputTextField.clear();
        imagesBox.getChildren().clear();
        try {
            File dataDir = new File(dataDirField.getText());
            dataDir.mkdir();
            File logFile;
            if(!experimentNameField.getText().equals("")) {
                logFile = new File(dataDir, experimentNameField.getText() + ".txt");
            } else {
                Date date = Calendar.getInstance().getTime();
                DateFormat dateFormat = new SimpleDateFormat("yyyy_mm_dd-hh_mm_ss");
                String strDate = dateFormat.format(date);
                logFile = new File(dataDir, "log_" + strDate + ".txt");
            }
            logFileName = logFile.getAbsolutePath();
            log = new FileOutputStream(logFile);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @FXML
    void startAction(ActionEvent event) {
        if(port != null) {
            System.out.println("Start");
            prepareForNewSerialInput();
            port.writeBytes(new byte[]{'s'}, 1);
            //port.getOutputStream().write(new byte[]{'s'});
        }
    }

    public void onCloseWindow() {
        if(port != null) {
            port.closePort();
        }
        if(log != null) {
            try {
                log.close();
                System.out.println("Save via close");
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

}

