import com.fazecast.jSerialComm.SerialPort;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.image.ImageView;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.*;

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
    private Pane imagesBox;

    @FXML
    private Parent afterConnectInterface;

    @FXML
    private TextField pythonField;

    @FXML
    private TextArea serialOutputTextField;

    @FXML
    private TextField startDelayField;

    @FXML
    private TextField frequencyField;

    @FXML
    private TextField timeCountField;

    @FXML
    private ToggleButton timeCountToggleButton;

    @FXML
    private ChoiceBox<Pair<Byte, String>> interfaceSelector;

    @FXML
    private ChoiceBox<Pair<SerialPort, String>> deviceSelector;

    private SerialPort port;
    private OutputStream log;
    private String logFileName;
    private String countedExperimentName;
    int baudRate = 115200;

    @FXML
    public void initialize() {
        scanForDevices();
        pythonField.setText("python");
        dataDirField.setText("data");
        scriptDirectoryField.setText("scripts");
        startDelayField.setText("0");
        timeCountField.setText("2");
        afterConnectInterface.setVisible(false);
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
        port.openPort();


        String frequencyLine = null;
        try(BufferedReader reader = getByteReaderForPort()) {
            writeStringToPort("F");
            Thread.sleep(100);
            frequencyLine = reader.readLine();
            reader.close();
            frequencyField.setText(frequencyLine.split(":")[1]);
        } catch (IOException e) {
            System.err.println("Failed to read frequency!");
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        afterConnectInterface.setVisible(true);
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
                ProcessBuilder processBuilder = new ProcessBuilder(
                        pythonField.getText(), scriptFile.getAbsolutePath(),
                        logFileName,
                        "-f", frequencyField.getText(),
                        timeCountToggleButton.isSelected()?"-c":"-t", timeCountField.getText(),
                        "-i", interfaceSelector.getValue()==null?"NONE":interfaceSelector.getValue().value);
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
            File moveTo = new File(new File(dataDirField.getText()), countedExperimentName);
            System.out.println("Moving named experiment to: "+moveTo.getAbsolutePath());
            boolean ok = scriptRunDirectory.renameTo(moveTo);
            System.out.println("moved: "+(ok?"True":"False"));
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
                countedExperimentName = experimentNameField.getText();
                logFile = new File(dataDir, countedExperimentName + ".txt");
                int i=1;
                while(logFile.exists()) {
                    countedExperimentName = experimentNameField.getText() + "_("+i+")";
                    logFile = new File(dataDir, countedExperimentName + ".txt");
                    i++;
                }
            } else {
                Date date = Calendar.getInstance().getTime();
                DateFormat dateFormat = new SimpleDateFormat("yyyy_MM_dd-HH_mm_ss");
                String strDate = dateFormat.format(date);
                countedExperimentName = "log_" + strDate;
                logFile = new File(dataDir, countedExperimentName + ".txt");
            }
            logFileName = logFile.getAbsolutePath();
            log = new FileOutputStream(logFile);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        port.removeDataListener();
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
    }

    public void writeStringToPort(String str) {
        byte[] data = str.getBytes(StandardCharsets.UTF_8);
        port.writeBytes(data, data.length);
    }

    public BufferedReader getByteReaderForPort() {
        port.removeDataListener();
        return new BufferedReader(new InputStreamReader(port.getInputStream()));
    }

    @FXML
    void scanForInterfacesAction(ActionEvent event) {

        try {
            BufferedReader reader = getByteReaderForPort();
            //while(reader.readLine()!=null) {} // clear out reader
            writeStringToPort("l");
            Thread.sleep(100);
            interfaceSelector.getItems().clear();
            while(true) {
                String line = reader.readLine();
                if(line.equals("e"))
                    break;
                System.out.println("Option: '"+line+"'");
                String[] parts = line.split(":");
                interfaceSelector.getItems().add(new Pair<>(parts[0].getBytes(StandardCharsets.UTF_8)[0], parts[1]));
            }
            reader.close();
        } catch (IOException e) {
            System.err.println("Failed to read available interfaces");
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    @FXML
    void SwitchTimeCountAction(ActionEvent event) {
        if(timeCountToggleButton.isSelected()) {
            timeCountToggleButton.setText("Count / (Time)");
        } else {
            timeCountToggleButton.setText("Time / (Count)");
        }
    }

    @FXML
    void setFrequencyAction(ActionEvent event) {
        writeStringToPort("f"+frequencyField.getText());
    }

    @FXML
    void startAction(ActionEvent event) {
        if(port != null) {
            if(!startDelayField.getText().equals("0")) {
                int delay = Integer.parseInt(startDelayField.getText());
                try {
                    if(delay > 30) {
                        delay = 30;
                        System.err.println("Limited delay to 30 secconds");
                    }
                    Thread.sleep(delay* 1000L);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            if(interfaceSelector.getValue() != null) {
                System.out.println("An Interface is selected");
                // set frequency

                StringBuffer startString = new StringBuffer();
                startString.append("f"+frequencyField.getText());
                // set interface
                startString.append("i"+(char)(byte)interfaceSelector.getValue().key);
                if(timeCountToggleButton.isSelected()) {
                    //count
                    startString.append("c"+timeCountField.getText());
                } else {
                    // time
                    startString.append("t"+timeCountField.getText());
                }
                prepareForNewSerialInput();
                startString.append("-");
                String command = startString.toString();
                System.out.println("Send start command: '"+command+"'");
                writeStringToPort(command);

            }
            else {
                System.out.println("Start");
                prepareForNewSerialInput();
                port.writeBytes(new byte[]{'s'}, 1);
                //port.getOutputStream().write(new byte[]{'s'});
            }
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

