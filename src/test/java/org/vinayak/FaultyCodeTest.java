package org.vinayak;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import org.junit.jupiter.api.Test;
import sootup.core.inputlocation.AnalysisInputLocation;
import sootup.core.jimple.common.stmt.Stmt;
import sootup.core.model.Body;
import sootup.core.model.SootClass;
import sootup.core.model.SootMethod;
import sootup.core.views.View;
import sootup.java.bytecode.inputlocation.PathBasedAnalysisInputLocation;
import sootup.java.core.views.JavaView;

public class FaultyCodeTest {
  @Test
  public void testAnalyzeBinaryAsmOld() {
    Path pathToBinary = Paths.get("src/test/resources/bytecode");
    AnalysisInputLocation inputLocation = PathBasedAnalysisInputLocation.create(pathToBinary, null);

    // Create a view for project, which allows us to retrieve classes
    View view = new JavaView(inputLocation);

    for (SootClass sootClass : view.getClasses()) {
      for (SootMethod method : sootClass.getMethods()) {
        System.out.println("Method: " + method.getSignature());
        Body body = method.getBody();

        List<Stmt> stmts = body.getStmts();

        for (Stmt stmt : stmts) {
          System.out.println(stmt);
        }
      }
    }
  }
}
