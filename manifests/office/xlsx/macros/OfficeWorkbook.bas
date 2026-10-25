Attribute VB_Name = "OfficeWorkbook"
Option Explicit

' Reviewed, manually imported standard module; no automatic entry or saving.
' Work on a backed-up working copy in native Excel. User confirmation belongs
' to the actual conversation, not Application.UserControl or a forged Boolean.
' The caller explicitly selects workbook/range and the approved operation.
' No Application.Run, workbook event, external refresh, trust setting, VBProject
' access, protection removal or all-open-workbooks calculation here. Calculation
' may evaluate formula-referenced UDFs: review those dependencies before approval.
' These procedures have static review only until run and checked in MS Excel.

Private Sub RequireOfficeRange(ByVal wb As Workbook, ByVal target As Range)
    If wb Is Nothing Then Err.Raise vbObjectError + 2401, "OfficeWorkbook", "Select an explicit working-copy workbook."
    If target Is Nothing Then Err.Raise vbObjectError + 2402, "OfficeWorkbook", "Select an explicit range."
    If Not (target.Parent.Parent Is wb) Then
        Err.Raise vbObjectError + 2403, "OfficeWorkbook", "Range belongs to another workbook."
    End If
End Sub

Private Sub RequireOfficeApproval(ByVal macroConfirmed As Boolean)
    If Not macroConfirmed Then
        Err.Raise vbObjectError + 2404, "OfficeWorkbook", "This selected macro operation is pending explicit approval."
    End If
End Sub

Public Sub CalculateOfficeRange(ByVal wb As Workbook, ByVal target As Range, _
                                Optional ByVal macroConfirmed As Boolean = False)
    ' Range.Calculate does not prove whole-workbook dependency/cached-value QA.
    ' Check cross-sheet precedents and business results separately after running.
    ' Approval includes review of this range's formula/UDF dependencies; disabling
    ' events is not a macro-security switch and does not suppress UDF evaluation.
    RequireOfficeApproval macroConfirmed
    RequireOfficeRange wb, target
    Dim previousEvents As Boolean, errorNumber As Long, errorText As String
    previousEvents = wb.Application.EnableEvents
    On Error GoTo Failed
    wb.Application.EnableEvents = False
    target.Calculate
    wb.Application.EnableEvents = previousEvents
    Exit Sub
Failed:
    errorNumber = Err.Number
    errorText = Err.Description
    wb.Application.EnableEvents = previousEvents
    Err.Raise errorNumber, "CalculateOfficeRange", errorText
End Sub

Public Sub ConfigureOfficePrintArea(ByVal wb As Workbook, ByVal view As Range, _
                                    Optional ByVal macroConfirmed As Boolean = False)
    ' Only the explicitly selected view; no implicit fit-to-page or font shrink.
    RequireOfficeApproval macroConfirmed
    RequireOfficeRange wb, view
    If view.Areas.Count <> 1 Then
        Err.Raise vbObjectError + 2405, "OfficeWorkbook", "Use one explicit contiguous delivery view."
    End If
    view.Worksheet.PageSetup.PrintArea = view.Address
    ' Printing/rendering every declared view remains a separate QA step.
End Sub

Public Function AddOfficeNativeChart(ByVal wb As Workbook, ByVal data As Range, _
                                      ByVal host As Worksheet, ByVal chartName As String, _
                                      ByVal title As String, ByVal chartConfirmed As Boolean, _
                                      Optional ByVal macroConfirmed As Boolean = False, _
                                      Optional ByVal chartType As XlChartType = xlColumnClustered, _
                                      Optional ByVal left As Double = 24, _
                                      Optional ByVal top As Double = 24, _
                                      Optional ByVal width As Double = 480, _
                                      Optional ByVal height As Double = 280) As ChartObject
    ' Two distinct approvals: run this selected macro AND create this new chart.
    ' False/no skips creation; pending should be resolved before calling VBA.
    RequireOfficeApproval macroConfirmed
    If Not chartConfirmed Then Exit Function
    RequireOfficeRange wb, data
    If host Is Nothing Then Err.Raise vbObjectError + 2406, "OfficeWorkbook", "Select a chart worksheet."
    If Not (host.Parent Is wb) Then Err.Raise vbObjectError + 2407, "OfficeWorkbook", "Chart sheet belongs to another workbook."
    If data.Areas.Count <> 1 Then Err.Raise vbObjectError + 2408, "OfficeWorkbook", "Chart data must be one explicit contiguous range."
    If Len(Trim$(chartName)) = 0 Or width <= 0 Or height <= 0 Then
        Err.Raise vbObjectError + 2409, "OfficeWorkbook", "Provide a chart name and positive dimensions."
    End If
    Dim existing As ChartObject
    For Each existing In host.ChartObjects
        If StrComp(existing.Name, chartName, vbTextCompare) = 0 Then
            Err.Raise vbObjectError + 2410, "OfficeWorkbook", "Existing chart is preserved; choose a new name."
        End If
    Next existing
    Dim created As ChartObject, previousEvents As Boolean
    Dim errorNumber As Long, errorText As String
    previousEvents = wb.Application.EnableEvents
    On Error GoTo Failed
    wb.Application.EnableEvents = False
    Set created = host.ChartObjects.Add(left, top, width, height)
    created.Name = chartName
    created.Chart.ChartType = chartType
    created.Chart.SetSourceData Source:=data, PlotBy:=xlColumns
    created.Chart.HasTitle = (Len(title) > 0)
    If Len(title) > 0 Then created.Chart.ChartTitle.Text = title
    Set AddOfficeNativeChart = created
    wb.Application.EnableEvents = previousEvents
    Exit Function
Failed:
    errorNumber = Err.Number
    errorText = Err.Description
    On Error Resume Next
    If Not created Is Nothing Then created.Delete
    wb.Application.EnableEvents = previousEvents
    On Error GoTo 0
    Err.Raise errorNumber, "AddOfficeNativeChart", errorText
End Function
