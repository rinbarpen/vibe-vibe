Attribute VB_Name = "OfficeLayout"
Option Explicit

' Reviewed, manually imported Word VBA standard module. Invoke only on a working copy.
' No AutoOpen/Document_Open entry point, saving, VBProject access, trust-setting
' changes, external program execution, revision acceptance or blanket protection.
' This code is statically checked on Linux; actual Word execution needs Word QA.
' Native references:
' https://learn.microsoft.com/en-us/office/vba/api/word.style
' https://learn.microsoft.com/en-us/office/vba/api/word.row.headingformat
' https://learn.microsoft.com/en-us/office/vba/api/word.document.repaginate
' https://learn.microsoft.com/en-us/office/vba/api/word.contentcontrol.lockcontents
' https://learn.microsoft.com/en-us/office/vba/api/word.contentcontrol.lockcontentcontrol

' Change these only for the current deliverable's approved typography.
Private Const BODY_FONT As String = "Noto Sans CJK SC"
Private Const BODY_SIZE_PT As Single = 11
Private Const CAPTION_SIZE_PT As Single = 9
Private Const SHORT_ROW_CHAR_LIMIT As Long = 180
Private Const SHORT_ROW_LINE_LIMIT As Long = 8
' Change only for an explicitly selected user/template multipage-table policy.
Private Const ALLOW_MULTIPAGE_TABLES As Boolean = False

Public Sub ApplyOfficeLayout()
    Dim doc As Document
    Dim table As Table
    Dim oldScreenUpdating As Boolean
    Dim failureNumber As Long
    Dim failureDescription As String
    Dim tableWarnings As Long

    Set doc = EditableWorkingDocument()
    If MsgBox("Apply the Office layout to this working copy? Existing content, " & _
        "tracked changes, control locks and fields remain. No file is saved.", _
        vbYesNo Or vbQuestion, "Office layout") <> vbYes Then Exit Sub
    oldScreenUpdating = Application.ScreenUpdating
    On Error GoTo Failed
    Application.ScreenUpdating = False

    FormatExistingStyle doc, wdStyleNormal, BODY_SIZE_PT, False
    FormatExistingStyle doc, wdStyleHeading1, 18, True
    FormatExistingStyle doc, wdStyleHeading2, 15, True
    FormatExistingStyle doc, wdStyleHeading3, 13, True
    FormatExistingStyle doc, wdStyleCaption, CAPTION_SIZE_PT, False
    For Each table In doc.Tables
        If Not FormatTable(table) Then tableWarnings = tableWarnings + 1
    Next table
    tableWarnings = tableWarnings + BindNativeCaptions(doc, ALLOW_MULTIPAGE_TABLES)
    RefreshNativeFields doc
    Application.ScreenUpdating = oldScreenUpdating
    MsgBox "Layout applied to the open working copy; no file was saved. " & _
        "Review every page, then Save As the required DOCX or DOCM. " & _
        "Tables needing manual review: " & CStr(tableWarnings), vbInformation, "Office layout"
    Exit Sub
Failed:
    failureNumber = Err.Number
    failureDescription = Err.Description
    Application.ScreenUpdating = oldScreenUpdating
    Err.Raise failureNumber, "OfficeLayout.ApplyOfficeLayout", failureDescription
End Sub

Public Sub UpdateOfficeFields()
    Dim doc As Document
    Set doc = EditableWorkingDocument()
    RefreshNativeFields doc
    MsgBox "Unlocked sequence/reference fields, indexes and pagination refreshed. " & _
        "Locked, externally linked and bibliography-manager fields were retained. Check field results and all pages; " & _
        "no file was saved.", vbInformation, "Office fields"
End Sub

Private Function EditableWorkingDocument() As Document
    If Documents.Count = 0 Then Err.Raise vbObjectError + 701, "OfficeLayout", "Open a working copy first."
    If ActiveDocument.ReadOnly Then Err.Raise vbObjectError + 702, "OfficeLayout", "The working copy is read-only."
    If ActiveDocument.ProtectionType <> wdNoProtection Then _
        Err.Raise vbObjectError + 703, "OfficeLayout", "Existing document protection remains; use the template owner's editing workflow."
    Set EditableWorkingDocument = ActiveDocument
End Function

Private Sub FormatExistingStyle(ByVal doc As Document, ByVal styleId As WdBuiltinStyle, _
        ByVal sizePt As Single, ByVal isHeading As Boolean)
    Dim targetStyle As Style
    Set targetStyle = doc.Styles(styleId)
    With targetStyle.Font
        .Name = BODY_FONT
        .NameFarEast = BODY_FONT
        .Size = sizePt
    End With
    With targetStyle.ParagraphFormat
        .WidowControl = True
        If isHeading Then
            .KeepWithNext = True
            .KeepTogether = True
        End If
    End With
    ' Styles belong to this Document, never NormalTemplate or AttachedTemplate.
    ' Custom styles, direct formatting, text, figure anchors and numbering stay intact.
End Sub

Private Function FormatTable(ByVal target As Table) As Boolean
    Dim currentRow As Row
    On Error GoTo NeedsReview
    If target.Rows.Count > 1 Then target.Rows(1).HeadingFormat = True
    For Each currentRow In target.Rows
        ' Do not force long or object-heavy rows onto a single page.
        ' Vertical-merge tables that Word cannot enumerate are reported for review.
        If Len(currentRow.Range.Text) <= SHORT_ROW_CHAR_LIMIT And _
                currentRow.Range.InlineShapes.Count = 0 Then
            If currentRow.Range.ComputeStatistics(wdStatisticLines) <= SHORT_ROW_LINE_LIMIT Then
                currentRow.AllowBreakAcrossPages = False
            End If
        End If
    Next currentRow
    FormatTable = True
    Exit Function
NeedsReview:
    Debug.Print "OfficeLayout table needs review: " & CStr(Err.Number) & " " & Err.Description
    FormatTable = False
End Function

Public Sub ApplyOfficeCaptionLayout()
    Dim doc As Document
    Dim pending As Long
    Set doc = EditableWorkingDocument()
    pending = BindNativeCaptions(doc, ALLOW_MULTIPAGE_TABLES)
    MsgBox "Caption keep constraints applied on the open working copy. " & _
        "Inspect every rendered page; no file was saved. Groups requiring review: " & _
        CStr(pending), vbInformation, "Office captions"
End Sub

Private Function CaptionSequence(ByVal target As Range) As String
    Dim item As Field
    Dim code As String
    Dim tokens() As String
    Dim candidate As String
    Dim matches As Long
    For Each item In target.Fields
        If item.Type = wdFieldSequence Then
            code = Trim(Replace(item.Code.Text, vbTab, " "))
            Do While InStr(code, "  ") > 0
                code = Replace(code, "  ", " ")
            Loop
            tokens = Split(code, " ")
            If UBound(tokens) >= 1 Then
                candidate = UCase(Replace(tokens(1), Chr(34), ""))
                If candidate = "FIGURE" Or candidate = "TABLE" Then
                    CaptionSequence = candidate
                    matches = matches + 1
                End If
            End If
        End If
    Next item
    If matches > 1 Then CaptionSequence = "AMBIGUOUS"
End Function

Private Function HasCaptionBoundary(ByVal target As Range, ByVal includeBefore As Boolean) As Boolean
    HasCaptionBoundary = (InStr(target.Text, Chr(12)) > 0 Or InStr(target.Text, Chr(14)) > 0)
    If includeBefore Then
        If target.ParagraphFormat.PageBreakBefore = True Then HasCaptionBoundary = True
    End If
End Function

Private Function FloatingShapeAt(ByVal doc As Document, ByVal target As Range) As Boolean
    Dim item As Shape
    For Each item In doc.Shapes
        If item.Anchor.Start >= target.Start And item.Anchor.Start < target.End Then
            FloatingShapeAt = True
            Exit Function
        End If
    Next item
End Function

Private Function AdjacentCaptionTable(ByVal doc As Document, ByVal caption As Range) As Table
    Dim remaining As Range
    Set remaining = doc.Range(caption.End, doc.Content.End)
    If remaining.Tables.Count > 0 Then
        If remaining.Tables(1).Range.Start = caption.End Then Set AdjacentCaptionTable = remaining.Tables(1)
    End If
End Function

Private Function GroupSpansPages(ByVal target As Range) As Boolean
    Dim first As Range
    Dim last As Range
    Set first = target.Duplicate
    first.Collapse wdCollapseStart
    Set last = target.Duplicate
    If last.End > last.Start Then last.End = last.End - 1
    last.Collapse wdCollapseEnd
    GroupSpansPages = (first.Information(wdActiveEndPageNumber) <> last.Information(wdActiveEndPageNumber))
End Function

Private Function BindNativeCaptions(ByVal doc As Document, ByVal allowMultipage As Boolean) As Long
    Dim caption As Paragraph
    Dim previous As Paragraph
    Dim target As Table
    Dim finalRow As Row
    Dim currentRow As Row
    Dim combined As Range
    Dim kind As String
    Dim residue As String
    Dim available As Single
    Dim minimum As Single
    Dim item As InlineShape
    Dim tableParagraph As Paragraph
    On Error GoTo NeedsReview
    For Each caption In doc.Paragraphs
        kind = CaptionSequence(caption.Range)
        If kind = "" Then GoTo NextCaption
        If kind = "AMBIGUOUS" Or caption.Range.StoryType <> wdMainTextStory Then GoTo PendingCaption
        If caption.Range.Information(wdWithInTable) Then GoTo PendingCaption
        If Not caption.Range.ParentContentControl Is Nothing Then GoTo PendingCaption
        With caption.Range.Sections(1).PageSetup
            available = .PageHeight - .TopMargin - .BottomMargin
        End With
        If kind = "FIGURE" Then
            Set previous = caption.Previous
            If previous Is Nothing Then GoTo PendingCaption
            If previous.Range.End <> caption.Range.Start Then GoTo PendingCaption
            If previous.Range.Information(wdWithInTable) Then GoTo PendingCaption
            If previous.Range.InlineShapes.Count = 0 Then GoTo PendingCaption
            If FloatingShapeAt(doc, previous.Range) Then GoTo PendingCaption
            If HasCaptionBoundary(previous.Range, False) Or HasCaptionBoundary(caption.Range, True) Then GoTo PendingCaption
            residue = previous.Range.Text
            residue = Replace(Replace(Replace(Replace(residue, Chr(1), ""), vbCr, ""), vbLf, ""), vbTab, "")
            If Len(Trim(residue)) > 0 Then GoTo PendingCaption
            For Each item In previous.Range.InlineShapes
                If item.Height > available Then GoTo PendingCaption
            Next item
            previous.Range.ParagraphFormat.KeepWithNext = True
            previous.Range.ParagraphFormat.KeepTogether = True
            caption.Range.ParagraphFormat.KeepTogether = True
            caption.Range.ParagraphFormat.KeepWithNext = False
            Set combined = doc.Range(previous.Range.Start, caption.Range.End)
        ElseIf kind = "TABLE" Then
            Set target = AdjacentCaptionTable(doc, caption.Range)
            If target Is Nothing Then GoTo PendingCaption
            If target.Title = "OfficeEquationLayout" Then GoTo PendingCaption
            If target.Range.Tables.Count <> 1 Then GoTo PendingCaption
            If target.Rows.WrapAroundText Then GoTo PendingCaption
            For Each tableParagraph In target.Range.Paragraphs
                If HasCaptionBoundary(tableParagraph.Range, True) Then GoTo PendingCaption
            Next tableParagraph
            If HasCaptionBoundary(caption.Range, False) Or HasCaptionBoundary(target.Range, True) Then GoTo PendingCaption
            minimum = 0
            For Each currentRow In target.Rows
                If currentRow.HeightRule <> wdRowHeightAuto Then minimum = minimum + currentRow.Height
            Next currentRow
            If Not allowMultipage And minimum > available Then GoTo PendingCaption
            Set finalRow = target.Rows(target.Rows.Count)
            caption.Range.ParagraphFormat.KeepTogether = True
            caption.Range.ParagraphFormat.KeepWithNext = True
            target.Rows.AllowBreakAcrossPages = False
            target.Range.ParagraphFormat.KeepWithNext = Not allowMultipage
            finalRow.Range.ParagraphFormat.KeepWithNext = False
            Set combined = doc.Range(caption.Range.Start, target.Range.End)
        End If
        doc.Repaginate
        If kind = "FIGURE" Or Not allowMultipage Then
            If GroupSpansPages(combined) Then GoTo PendingCaption
        End If
        GoTo NextCaption
PendingCaption:
        BindNativeCaptions = BindNativeCaptions + 1
        Debug.Print "Office caption pending: " & kind & " at " & CStr(caption.Range.Start)
NextCaption:
    Next caption
    Exit Function
NeedsReview:
    Debug.Print "Office captions need review: " & CStr(Err.Number) & " " & Err.Description
    BindNativeCaptions = BindNativeCaptions + 1
End Function

Private Sub RefreshNativeFields(ByVal doc As Document)
    Dim toc As TableOfContents
    Dim figures As TableOfFigures
    Dim nativeIndex As Object
    Dim updateFailures As Long

    ' Dependency order matters: a forward REF can otherwise cache the old SEQ.
    updateFailures = UpdateFieldPass(doc, 0)  ' Resolve chapter-style prefixes first.
    updateFailures = updateFailures + UpdateFieldPass(doc, 1)  ' All unlocked SEQ numbers next.
    updateFailures = updateFailures + UpdateFieldPass(doc, 2)  ' REF/internal content next.
    doc.Repaginate
    For Each toc In doc.TablesOfContents
        If Not FirstFieldIsLocked(toc.Range) Then toc.Update
    Next toc
    For Each figures In doc.TablesOfFigures
        If Not FirstFieldIsLocked(figures.Range) Then figures.Update
    Next figures
    For Each nativeIndex In doc.Indexes
        If Not FirstFieldIsLocked(nativeIndex.Range) Then nativeIndex.Update
    Next nativeIndex
    For Each nativeIndex In doc.TablesOfAuthorities
        If Not FirstFieldIsLocked(nativeIndex.Range) Then nativeIndex.Update
    Next nativeIndex
    ' Updated indexes can change pagination; refresh page-dependent fields last.
    doc.Repaginate
    updateFailures = updateFailures + UpdateFieldPass(doc, 3)
    updateFailures = updateFailures + UpdateFieldPass(doc, 2)  ' Rebind REF after page-local STYLEREF.
    For Each toc In doc.TablesOfContents
        If Not FirstFieldIsLocked(toc.Range) Then toc.UpdatePageNumbers
    Next toc
    For Each figures In doc.TablesOfFigures
        If Not FirstFieldIsLocked(figures.Range) Then figures.UpdatePageNumbers
    Next figures
    If updateFailures > 0 Then Err.Raise vbObjectError + 704, "OfficeLayout", _
        CStr(updateFailures) & " field updates failed. Inspect results before delivery."
End Sub

Private Function UpdateFieldPass(ByVal doc As Document, ByVal passKind As Long) As Long
    Dim story As Range
    Dim current As Range
    Dim item As Field
    Dim selected As Boolean
    For Each story In doc.StoryRanges
        Set current = story
        Do
            For Each item In current.Fields
                If Not item.Locked And IsInternalField(item) Then
                    Select Case passKind
                        Case 0
                            selected = (item.Type = wdFieldStyleRef)
                        Case 1
                            selected = (item.Type = wdFieldSequence)
                        Case 2
                            selected = (item.Type = wdFieldRef)
                        Case 3
                            selected = IsPageDependentField(item)
                        Case Else
                            selected = False
                    End Select
                    If selected Then
                        If Not item.Update Then UpdateFieldPass = UpdateFieldPass + 1
                    End If
                End If
            Next item
            Set current = current.NextStoryRange
        Loop Until current Is Nothing
    Next story
End Function

Private Function IsPageDependentField(ByVal item As Field) As Boolean
    Select Case item.Type
        Case wdFieldPage, wdFieldPageRef, wdFieldNumPages, wdFieldSectionPages, wdFieldStyleRef
            IsPageDependentField = True
        Case Else
            IsPageDependentField = False
    End Select
End Function

Private Function IsIndexField(ByVal item As Field) As Boolean
    Select Case item.Type
        Case wdFieldTOC, wdFieldIndex, wdFieldTOA
            IsIndexField = True
        Case Else
            IsIndexField = False
    End Select
End Function

Private Function FirstFieldIsLocked(ByVal target As Range) As Boolean
    If target.Fields.Count > 0 Then FirstFieldIsLocked = target.Fields(1).Locked
End Function

Private Function IsInternalField(ByVal item As Field) As Boolean
    Select Case item.Type
        Case wdFieldDDE, wdFieldDDEAuto, wdFieldDatabase, wdFieldIncludePicture, _
                wdFieldIncludeText, wdFieldLink, wdFieldImport, wdFieldInclude, wdFieldRefDoc, _
                wdFieldAddin, wdFieldCitation, wdFieldBibliography
            IsInternalField = False
        Case Else
            IsInternalField = True
    End Select
End Function

Public Sub ProtectSelectedTemplateControl()
    Dim doc As Document
    Dim control As ContentControl
    Dim choice As VbMsgBoxResult
    Set doc = EditableWorkingDocument()
    Set control = Selection.ParentContentControl
    If control Is Nothing Then Err.Raise vbObjectError + 705, "OfficeLayout", "Place the cursor inside the intended content control."
    choice = MsgBox("Protect only this selected content control?" & vbCrLf & _
        "Yes: prevent deletion and content editing." & vbCrLf & _
        "No: prevent deletion, keep its contents editable." & vbCrLf & _
        "Cancel: leave it unchanged. This is an editing constraint, not access control.", _
        vbYesNoCancel Or vbQuestion, "Selected template control")
    If choice = vbCancel Then Exit Sub
    control.LockContentControl = True
    control.LockContents = (choice = vbYes)
End Sub

Public Sub RemoveSelectedTemplateControlLocks()
    Dim doc As Document
    Dim control As ContentControl
    Set doc = EditableWorkingDocument()
    Set control = Selection.ParentContentControl
    If control Is Nothing Then Err.Raise vbObjectError + 705, "OfficeLayout", "Place the cursor inside the intended content control."
    If MsgBox("Remove editing and deletion locks only from this selected control?", _
        vbYesNo Or vbQuestion, "Selected template control") <> vbYes Then Exit Sub
    control.LockContents = False
    control.LockContentControl = False
End Sub
