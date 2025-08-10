package org.vinayak;

import java.util.List;
import javax.annotation.Nonnull;
import sootup.core.jimple.common.expr.AbstractInvokeExpr;
import sootup.core.jimple.common.stmt.JInvokeStmt;
import sootup.core.jimple.common.stmt.Stmt;
import sootup.core.jimple.visitor.*;
import sootup.core.types.ClassType;
import sootup.core.views.View;

class StmtClientVisitor extends AbstractStmtVisitor<StmtVisitor> {
  private final View view;
  private final List<String> externalMethodCalls;

  public StmtClientVisitor(View view, List<String> externalMethodCalls) {
    this.view = view;
    this.externalMethodCalls = externalMethodCalls;
  }

  @Override
  public void defaultCaseStmt(@Nonnull Stmt stmt) {
    if (stmt.containsInvokeExpr()) {
      AbstractInvokeExpr invokeStmt = stmt.getInvokeExpr();
      ClassType classType = invokeStmt.getMethodSignature().getDeclClassType();
      boolean isInternal = view.getClass(classType).isPresent();
      if (!isInternal) {
        externalMethodCalls.add(invokeStmt.getMethodSignature().toString());
      }
    }
  }

  @Override
  public void caseInvokeStmt(@Nonnull JInvokeStmt stmt) {
    JInvokeStmt invokeStmt = stmt;
    ClassType classType = invokeStmt.getInvokeExpr().getMethodSignature().getDeclClassType();
    boolean isInternal = view.getClass(classType).isPresent();
    if (!isInternal) {
      externalMethodCalls.add(invokeStmt.getInvokeExpr().getMethodSignature().toString());
    }
  }
}
