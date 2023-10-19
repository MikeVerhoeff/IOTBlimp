import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;

public class Application extends javafx.application.Application {

    public static void start(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) throws IOException {

        FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource("main.fxml"));
        Parent root = fxmlLoader.load();
        Controller controller = (Controller) fxmlLoader.getController();

        System.out.println(controller);

        Scene scene = new Scene(root);

        stage.setOnCloseRequest((e)->controller.onCloseWindow());
        stage.setTitle("Experiment data collector");
        stage.setScene(scene);
        stage.show();
    }
}
