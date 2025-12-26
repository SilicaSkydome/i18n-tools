# 🧪 Testing Guide - i18n Manager v3.0

This guide helps you test the completely refactored standalone application.

## ✅ Pre-Testing Checklist

1. **Python Version**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Dependencies**
   ```bash
   pip install deep-translator
   # Or just run the app - it auto-installs!
   ```

3. **Backup Your Project**
   - Make a git commit before testing
   - Or create a backup copy of your project

## 🎯 Test Scenarios

### Test 1: Application Launch

**Expected:**
- GUI opens without errors
- Window title: "i18n Manager - Universal Translation Tool"
- All UI elements visible and styled correctly
- Progress panel shows welcome message

**Steps:**
```bash
python i18n_manager.py
```

**Success Criteria:**
✅ Application opens
✅ Modern styling visible (blue header, styled buttons)
✅ No error messages in console
✅ Welcome message appears in output panel

---

### Test 2: Project Selection (Existing i18n)

**Prerequisites:** Use a React project that already has i18n configured

**Steps:**
1. Click "📂 Browse" button
2. Select your React project folder
3. Wait for detection

**Expected:**
- "✅ i18n configured - Ready to use" status
- Source directory detected (e.g., "✓ Found source: src/")
- Existing languages auto-detected and checkboxes checked
- "🚀 Run Complete Workflow" button enabled

**Success Criteria:**
✅ Project path displayed correctly
✅ i18n status shows green checkmark
✅ Existing languages detected
✅ Workflow button becomes active

---

### Test 3: Project Selection (NO i18n)

**Prerequisites:** Use a React project WITHOUT i18n setup

**Steps:**
1. Click "📂 Browse" button
2. Select a React project without i18n
3. Wait for detection

**Expected:**
- "⚠️ i18n not configured" status
- Popup asks: "Setup i18n?"
- Setup wizard opens if you click "Yes"

**Success Criteria:**
✅ Detects missing i18n setup
✅ Offers to configure it
✅ Wizard opens on confirmation

---

### Test 4: i18n Setup Wizard

**Prerequisites:** Project without i18n setup

**Steps:**
1. Select project without i18n
2. Click "Yes" when prompted
3. Review wizard content
4. Click "Create Setup"

**Expected:**
- Wizard shows 2 steps:
  - Step 1: Install Dependencies (shows npm install command)
  - Step 2: Files Created (shows directory structure)
- After clicking "Create Setup":
  - Files created in project:
    - `src/i18n/config.ts`
    - `src/i18n/index.ts`
    - `src/i18n/locales/en.json` (and other selected languages)
  - Success message with next steps
  - Status updates to "✅ i18n configured"

**Success Criteria:**
✅ Wizard displays correctly
✅ Files created in correct locations
✅ Files have proper content (check manually)
✅ Success dialog appears
✅ Status updates automatically

---

### Test 5: Language Selection

**Steps:**
1. Select project
2. Check/uncheck various language checkboxes
3. Observe "Selected" count update

**Expected:**
- English always checked (disabled checkbox)
- Other languages can be toggled
- Count updates in real-time
- Languages grouped in 3 columns

**Success Criteria:**
✅ English cannot be unchecked
✅ Other languages toggle properly
✅ Count displays: "Selected (X): Language1, Language2..."
✅ UI is scrollable for many languages

---

### Test 6: Step 1 - Detect Text

**Steps:**
1. Select configured project
2. Click "1️⃣ Detect Text" button
3. Watch progress

**Expected:**
- Button disables during execution
- Progress bar animates
- Output shows:
  - Files scanned
  - Number of strings found
  - Preview of first 10 strings
- "2️⃣ Generate Keys" button enables after completion

**Success Criteria:**
✅ Progress indication works
✅ Finds hardcoded text (if any exists)
✅ Shows preview in output panel
✅ Next button enables
✅ No errors in console

---

### Test 7: Step 2 - Generate Keys

**Prerequisites:** Completed Step 1 (Detect)

**Steps:**
1. Click "2️⃣ Generate Keys" button
2. Watch progress

**Expected:**
- Keys generated with semantic names
- Grouped by section (nav, home, button, etc.)
- Output shows:
  - Number of keys generated
  - Keys by section breakdown
- "3️⃣ Translate" button enables

**Success Criteria:**
✅ Keys have good names (camelCase)
✅ Keys are grouped logically
✅ Output is readable and informative
✅ Translation button enables

---

### Test 8: Step 3 - Translate

**Prerequisites:** Completed Steps 1-2

**Steps:**
1. Select 2-3 languages
2. Click "3️⃣ Translate" button
3. Wait (this may take a few minutes)

**Expected:**
- Warning: "⏳ This may take a few minutes..."
- Real-time translation progress
- Output shows each language being translated
- Language files updated with translations
- "4️⃣ Replace Code" button enables

**Success Criteria:**
✅ Translation progress visible
✅ Multiple languages translated
✅ Files updated: `src/i18n/locales/*.json`
✅ Translations are accurate (spot check)
✅ No rate limit errors

---

### Test 9: Step 4 - Replace Code

**Prerequisites:** Completed Steps 1-3

**Steps:**
1. Click "4️⃣ Replace Code" button
2. Review confirmation dialog
3. Click "Yes" to proceed
4. Watch progress

**Expected:**
- Confirmation dialog shows file count
- Progress indication during replacement
- Output shows:
  - Files modified
  - Backup location
- Success message
- Final dialog with statistics

**Success Criteria:**
✅ Confirmation required before changes
✅ Backups created in `.backups/` folder
✅ Source files updated correctly
✅ `useTranslation` import added
✅ `const { t } = useTranslation()` added
✅ Text replaced with `{t("key")}` calls
✅ Syntax remains valid (check manually)

---

### Test 10: Complete Workflow (All at Once)

**Steps:**
1. Fresh project selection
2. Select 3+ languages
3. Click "🚀 Run Complete Workflow"
4. Confirm in dialog
5. Wait for completion (may take 5-10 minutes)

**Expected:**
- Single confirmation dialog
- All 4 steps execute automatically:
  1. Detection
  2. Key generation
  3. Translation (with progress)
  4. Code replacement
- Final success dialog with full statistics

**Success Criteria:**
✅ All steps complete without errors
✅ Progress visible throughout
✅ Output shows all steps
✅ Files modified correctly
✅ Backups created
✅ Project builds successfully after changes

---

## 🔍 Manual Verification

After running workflow, manually check:

### 1. Translation Files
```bash
# Check files were created
ls src/i18n/locales/

# Should show: en.json, es.json, fr.json, etc.

# Check content
cat src/i18n/locales/en.json
# Should show organized sections with English text

cat src/i18n/locales/es.json
# Should show Spanish translations
```

### 2. Source Code Changes
```bash
# Check a modified file
cat src/pages/Home.tsx
# Should have:
# - import { useTranslation } from 'react-i18next';
# - const { t } = useTranslation();
# - {t("section.key")} instead of hardcoded text
```

### 3. Backups
```bash
# Check backups exist
ls i18n-tools/.backups/

# Should show timestamped folder like: 20251225_143022/
# Contains original versions of modified files
```

### 4. Build & Run
```bash
# Your project should still build
npm run build

# And run without errors
npm run dev
```

## 🐛 Common Issues & Solutions

### Issue: "No source directory found"

**Cause:** Project doesn't have `src/`, `app/`, `client/`, or `frontend/` folder

**Solution:** 
- Ensure your project has a standard structure
- Or modify the detection logic in `detect_project_setup()`

---

### Issue: Translation fails with rate limit error

**Cause:** Too many API requests to Google Translate

**Solution:**
- Translate fewer languages at once
- Wait 1-2 minutes between attempts
- Consider using fewer strings in test project

---

### Issue: Code syntax breaks after replacement

**Cause:** Edge case in replacement patterns

**Solution:**
- Check `.backups/` folder for original files
- Restore affected files
- Report the specific case for fixing
- Manually fix the broken syntax

---

### Issue: GUI freezes during operation

**Cause:** Threading not working properly

**Solution:**
- Check console for errors
- Ensure `threading` import is working
- Try smaller project for testing

---

### Issue: Dependencies don't auto-install

**Cause:** pip not in PATH or restricted permissions

**Solution:**
```bash
pip install deep-translator
# Or
python -m pip install deep-translator
```

---

## 📊 Test Results Template

Use this template to track testing:

```
i18n Manager v3.0 - Test Results
=================================

Date: ___________
Python Version: ___________
OS: ___________

[ ] Test 1: Application Launch
[ ] Test 2: Project Selection (Existing i18n)
[ ] Test 3: Project Selection (NO i18n)
[ ] Test 4: i18n Setup Wizard
[ ] Test 5: Language Selection
[ ] Test 6: Step 1 - Detect Text
[ ] Test 7: Step 2 - Generate Keys
[ ] Test 8: Step 3 - Translate
[ ] Test 9: Step 4 - Replace Code
[ ] Test 10: Complete Workflow

Manual Verification:
[ ] Translation files created
[ ] Source code updated correctly
[ ] Backups exist
[ ] Project builds successfully
[ ] Application runs without errors

Issues Found:
1. _______________________________
2. _______________________________
3. _______________________________

Overall Status: [ PASS / FAIL ]
```

## 🎉 Success Indicators

You know testing succeeded when:

✅ All tests pass without errors
✅ Project builds and runs correctly
✅ Translations display in UI when language is switched
✅ No syntax errors in modified files
✅ Backups are intact
✅ Tool is responsive and doesn't freeze

## 📝 Next Steps After Testing

1. **If all tests pass:**
   - Start using on real projects!
   - Keep backups just in case
   - Report any edge cases found

2. **If tests fail:**
   - Note which test failed
   - Check console for error messages
   - Review backups to restore if needed
   - Report issues with details

3. **For production use:**
   - Always commit before running
   - Test on a branch first
   - Review changes before merging
   - Keep tool updated

---

Happy Testing! 🚀
