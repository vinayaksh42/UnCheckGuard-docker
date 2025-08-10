package org.vinayak;

import java.util.List;
import java.util.Set;
import javax.annotation.Nonnull;
import sootup.core.jimple.basic.Local;
import sootup.core.jimple.basic.Value;
import sootup.core.jimple.common.expr.JNewExpr;
import sootup.core.jimple.common.stmt.JAssignStmt;
import sootup.core.jimple.common.stmt.JThrowStmt;
import sootup.core.jimple.visitor.*;
import sootup.core.model.Body;
import sootup.core.typehierarchy.TypeHierarchy;
import sootup.core.types.ClassType;
import sootup.java.core.jimple.basic.JavaLocal;

class StmtCallGraphVisitor extends AbstractStmtVisitor<StmtVisitor> {
  private final TypeHierarchy typeHierarchy;
  private final Body.BodyBuilder bodyBuilder;
  private final List<String> uncheckedExceptions;
  private final String MethodSignature;
  private final List<String> sinkForFlowDroid;
  static final String JAVA_LANG_RUNTIME_EXCEPTION = "java.lang.RuntimeException";
  static final String JAVA_LANG_ERROR = "java.lang.Error";

  public StmtCallGraphVisitor(
      TypeHierarchy typeHierarchy,
      Body.BodyBuilder bodyBuilder,
      List<String> uncheckedExceptions,
      String MethodSignature,
      List<String> sinkForFlowDroid) {
    this.typeHierarchy = typeHierarchy;
    this.bodyBuilder = bodyBuilder;
    this.uncheckedExceptions = uncheckedExceptions;
    this.MethodSignature = MethodSignature;
    this.sinkForFlowDroid = sinkForFlowDroid;
  }

  @Override
  public void caseAssignStmt(@Nonnull JAssignStmt stmt) {
    JAssignStmt assignStmt = stmt;
    Value rhs = assignStmt.getRightOp();
    Value lhs = assignStmt.getLeftOp();
    if (rhs instanceof JNewExpr && lhs instanceof Local) {
      JNewExpr newExpr = (JNewExpr) rhs;
      JavaLocal stackTrace = (JavaLocal) lhs;
      Local local = new Local(stackTrace.getName(), newExpr.getType());
      bodyBuilder.replaceLocal(stackTrace, local);
    }
  }

  @Override
  public void caseThrowStmt(@Nonnull JThrowStmt stmt) {
    JThrowStmt throwStmt = stmt;

    JavaLocal stackName;
    try {
      stackName = (JavaLocal) throwStmt.getOp();
    } catch (ClassCastException e) {
      System.err.println("Error: throwStmt.getOp() is not of type JavaLocal. Aborting operation.");
      return;
    }

    Set<Local> locals = bodyBuilder.getLocals();
    for (Local local : locals) {
      if (local.getName().equals(stackName.getName())) {
        ClassType type = (ClassType) stackName.getType();
        ClassType superClass = typeHierarchy.superClassOf(type).get();
        if (type.getFullyQualifiedName().equals(JAVA_LANG_RUNTIME_EXCEPTION)
            || superClass.getFullyQualifiedName().equals(JAVA_LANG_RUNTIME_EXCEPTION)
            || type.getFullyQualifiedName().equals(JAVA_LANG_ERROR)
            || superClass.getFullyQualifiedName().equals(JAVA_LANG_ERROR)) {
          String exception = type.toString() + " " + MethodSignature;
          uncheckedExceptions.add(exception);
          sinkForFlowDroid.add(type.toString() + ": void &lt;init&gt;()");
          sinkForFlowDroid.add(
              type.toString() + ": void &lt;init&gt;(java.lang.String,java.lang.Throwable)");
          sinkForFlowDroid.add(type.toString() + ": void &lt;init&gt;(java.lang.String)");
          sinkForFlowDroid.add(type.toString() + ": void &lt;init&gt;(java.lang.Throwable)");
        }
      }
    }
  }
}
