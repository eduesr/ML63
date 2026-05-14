# Profile Modal - Manual Testing Guide

## Overview
This guide provides step-by-step instructions for manually testing the profile modal implementation with live Supabase data. The core logic has been verified (26/26 tests passed), and this guide covers functional testing in an actual browser environment.

## Prerequisites
1. ML63.html is served over HTTP (not file://)
   - HTTP server is running on port 8000
   - Access at: http://localhost:8000/ML63.html
2. Supabase project is properly configured
   - `user_roles` table exists with test data
   - `user_profiles` table exists or will be created on first save
   - Supabase credentials are configured in ML63.html
3. Test user accounts exist in Supabase Auth
   - At least one admin user (test.admin@example.com)
   - At least one viewer user (test.viewer@example.com)

## Core Logic Tests Summary
✅ **26/26 Logic Tests Passed**
- Avatar color logic for admin/viewer roles
- Name validation (empty, spaces, valid input)
- Avatar initial generation from email
- Modal state management (open/close)
- Role display formatting with emojis
- File validation for image uploads
- Toast notification messages

## Manual Testing Scenarios

### Test 1: Authentication & Avatar Display
**Objective**: Verify user authentication triggers avatar display and profile data loading

**Steps**:
1. Open http://localhost:8000/ML63.html in your browser
2. Click the login button and authenticate with a test admin account (test.admin@example.com)
3. Wait for the app to load
4. Observe the top-right corner of the header

**Expected Results**:
- [ ] Avatar button appears in top-right with user's first initial (T for test.admin@example.com)
- [ ] Avatar background color is purple (#4F46E5) for admin users
- [ ] Avatar button is clickable

**Notes**:
- Check browser console (F12 → Console) for any errors
- Verify Supabase authentication is working by checking for "Authenticated" status

---

### Test 2: Avatar Dropdown Menu
**Objective**: Verify the avatar dropdown menu opens and displays correct information

**Steps**:
1. Click the avatar button in the top-right
2. Observe the dropdown menu
3. Check all displayed information

**Expected Results**:
- [ ] Dropdown menu appears below avatar button
- [ ] User email address is displayed (test.admin@example.com)
- [ ] User role is shown with emoji (⚙️ Administrador for admin, 👁️ Visualizador for viewer)
- [ ] Two buttons are present: "👤 Mi perfil" and "🚪 Cerrar sesión"
- [ ] Dropdown closes when clicking outside it

**Notes**:
- The user name might show as the email username if no profile name has been saved yet
- Test dismissing the dropdown by clicking elsewhere on the page

---

### Test 3: Opening Profile Modal
**Objective**: Verify the profile modal opens correctly

**Steps**:
1. Click the avatar button
2. Click "👤 Mi perfil" in the dropdown
3. Observe the modal that appears

**Expected Results**:
- [ ] Modal overlay appears with semi-transparent dark background
- [ ] Modal is centered on the screen
- [ ] Modal contains all required fields:
  - Avatar preview with initials and role-based color
  - "Nombre" (Name) - editable text input
  - "Rol" (Role) - read-only display
  - "Email" - read-only display
  - "Cambiar avatar" button
  - "Cancelar" button
  - "Guardar cambios" button
- [ ] Close button (✕) is visible in top-right corner

**Notes**:
- The modal should slide in or fade in (depending on CSS implementation)
- Verify the modal is properly focused for accessibility

---

### Test 4: Profile Data Population
**Objective**: Verify profile modal populates with current user data

**Steps**:
1. Open the profile modal (see Test 3)
2. Check each field's content

**Expected Results**:
- [ ] Avatar preview shows correct initial (T) and role-based color (purple for admin)
- [ ] Name field is populated with saved name (or empty if first time)
- [ ] Role field shows "⚙️ Administrador" for admin users
- [ ] Email field shows the user's email address (test.admin@example.com)

**Notes**:
- If this is the user's first time opening the profile, the name field may be empty
- The role and email fields should not be editable
- Check browser console for any data loading errors

---

### Test 5: Avatar Image Preview
**Objective**: Verify avatar image preview functionality

**Prerequisites**:
- Profile modal is open
- You have an image file on your computer

**Steps**:
1. Click "Cambiar avatar" button
2. Select a JPG, PNG, GIF, or WebP image file (try different formats)
3. Observe the avatar preview area

**Expected Results**:
- [ ] File picker dialog opens
- [ ] Selected image displays in avatar preview
- [ ] Image fills the circular preview area (background-size: cover)
- [ ] Initials disappear when image is loaded
- [ ] Image persists until form is submitted or modal is closed

**Edge Cases to Test**:
- [ ] Try selecting a large image (>5MB) - verify it still loads
- [ ] Try selecting a small image - verify scaling works
- [ ] Try different image formats (JPG, PNG, GIF, WebP)
- [ ] Try selecting a non-image file (PDF, TXT) - verify it's rejected by accept="image/*"

**Notes**:
- The image is only previewed locally; it's not saved until you click "Guardar cambios"
- The preview uses CSS background-size: cover to maintain aspect ratio

---

### Test 6: Read-Only Fields Validation
**Objective**: Verify that role and email fields are truly read-only

**Steps**:
1. Open profile modal
2. Try clicking on the "Rol" field
3. Try clicking on the "Email" field
4. Attempt to type in each field

**Expected Results**:
- [ ] Role field is not editable (styled as div, not input)
- [ ] Email field is not editable (styled as div, not input)
- [ ] Email field shows warning message: "⚠️ Para cambiar tu email, contacta con administración"
- [ ] No text cursor appears in these fields
- [ ] Cannot modify these fields with keyboard or mouse

**Notes**:
- These fields are intentionally read-only for security reasons
- Users must contact an administrator to change email/role

---

### Test 7: Name Field Editing
**Objective**: Verify the name field is editable

**Steps**:
1. Open profile modal
2. Click on the "Nombre" (Name) field
3. Clear the existing content
4. Type a new name

**Expected Results**:
- [ ] Name field is clickable and focusable
- [ ] Text can be selected and deleted
- [ ] New text appears in real-time as you type
- [ ] Field shows input cursor
- [ ] Field accepts special characters, accents, and multiple words

**Notes**:
- The name field should accept any reasonable text input
- Test with Spanish characters (ñ, á, é, í, ó, ú)

---

### Test 8: Save Profile Changes - Success
**Objective**: Verify successful save with valid data

**Prerequisites**:
- Profile modal is open
- You have entered a valid name

**Steps**:
1. Modify the name field with a new value (e.g., "Updated Name " + current timestamp)
2. Click "Guardar cambios" button
3. Observe the response

**Expected Results**:
- [ ] Green success toast notification appears: "✓ Perfil actualizado"
- [ ] Modal closes automatically after 2 seconds
- [ ] Avatar dropdown now shows the updated name
- [ ] No errors in browser console

**Verification Steps**:
1. [ ] Close and reopen the profile modal
2. [ ] Verify the name still shows the updated value
3. [ ] Refresh the page (Cmd+R or Ctrl+R)
4. [ ] Verify the name persists after page reload

**Notes**:
- The toast notification should display for 3-5 seconds before disappearing
- Changes should be immediately visible in the UI
- Changes should persist to Supabase database

---

### Test 9: Save Profile Changes - Validation Error
**Objective**: Verify validation prevents saving empty name

**Steps**:
1. Open profile modal
2. Clear the "Nombre" field completely (delete all text)
3. Click "Guardar cambios" button
4. Observe the response

**Expected Results**:
- [ ] Red error toast notification appears: "El nombre es obligatorio"
- [ ] Modal remains open (doesn't close)
- [ ] No data is saved to Supabase
- [ ] Name field is still visible and can be edited

**Test Case Variations**:
- [ ] Name field is completely empty
- [ ] Name field contains only spaces
- [ ] Name field contains a single character (should work)
- [ ] Name field contains very long text (>100 characters - should work)

**Notes**:
- Validation should trim whitespace before checking if name is empty
- Error toast should display clearly in red/warning color

---

### Test 10: Closing Profile Modal
**Objective**: Verify all ways to close the modal work correctly

**Steps - Method 1: Cancel Button**:
1. Click "Cancelar" button
2. Verify modal closes

**Steps - Method 2: Close Button (✕)**:
1. Open modal again
2. Click the "✕" button in top-right corner
3. Verify modal closes

**Steps - Method 3: Overlay Click**:
1. Open modal again
2. Click on the dark overlay area (not on modal content)
3. Verify modal closes

**Steps - Method 4: Escape Key**:
1. Open modal again
2. Press Escape key (ESC)
3. Verify modal closes

**Expected Results**:
- [ ] All close methods work correctly
- [ ] Modal closes without saving unsaved changes
- [ ] File input is reset (avatar upload input cleared)
- [ ] Modal returns to hidden state

**Notes**:
- Test each close method independently
- Verify unsaved changes are discarded when using different close methods
- Check that avatar preview is cleared when modal closes

---

### Test 11: Admin vs Viewer Behavior
**Objective**: Verify consistent behavior between admin and viewer roles

**Prerequisites**:
- Test accounts for both admin and viewer roles exist

**Steps**:
1. Log in as admin user (test.admin@example.com)
2. Open profile modal
3. Note avatar color and role display
4. Log out
5. Log in as viewer user (test.viewer@example.com)
6. Open profile modal
7. Note avatar color and role display

**Expected Results - Admin**:
- [ ] Avatar color is purple (#4F46E5)
- [ ] Role displays "⚙️ Administrador"
- [ ] Can edit name and save changes

**Expected Results - Viewer**:
- [ ] Avatar color is green (#10B981)
- [ ] Role displays "👁️ Visualizador"
- [ ] Can edit name and save changes

**Notes**:
- Both roles should have identical functionality
- Only the avatar color and role text should differ
- Verify both roles can save profile changes

---

### Test 12: Concurrent User Sessions
**Objective**: Verify profile data isolation between users

**Steps**:
1. Open two browser windows or tabs
2. In Window A: Log in as User A (test.admin@example.com)
3. In Window B: Log in as User B (test.viewer@example.com)
4. In Window A: Open profile modal and change name to "User A " + timestamp
5. In Window A: Save changes
6. In Window B: Open profile modal and observe the data
7. In Window B: Change name to "User B " + timestamp
8. In Window B: Save changes
9. Return to Window A and verify it still shows User A's data

**Expected Results**:
- [ ] Each session maintains independent profile data
- [ ] User A's changes don't affect User B's profile
- [ ] Each user sees their own data in the modal
- [ ] Supabase correctly associates data with each email

**Notes**:
- Use different timestamps in names to verify data wasn't swapped
- Refresh each page and verify data persists correctly

---

### Test 13: Cross-Browser Testing
**Objective**: Verify profile modal works across different browsers

**Test Browsers**:
- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest) - if available
- [ ] Edge (latest) - if available
- [ ] Mobile browsers (iOS Safari, Chrome Mobile) - if available

**Steps for Each Browser**:
1. Open http://localhost:8000/ML63.html
2. Authenticate with test account
3. Test all profile modal functionality:
   - Open avatar dropdown
   - Open profile modal
   - Edit avatar image
   - Edit name
   - Save changes
   - Close modal

**Expected Results**:
- [ ] All features work consistently across browsers
- [ ] No console errors in any browser
- [ ] Styling appears correct (colors, spacing, fonts)
- [ ] Touch events work properly on mobile browsers

**Notes**:
- Check browser developer tools (F12) for errors
- Test with different zoom levels if possible

---

### Test 14: Responsive Design Testing
**Objective**: Verify modal is usable on different screen sizes

**Test Viewports**:
Use browser DevTools to resize viewport:
- [ ] Desktop: 1920x1080
- [ ] Laptop: 1366x768
- [ ] Tablet: 768x1024 (iPad portrait)
- [ ] Mobile: 375x812 (iPhone 12)
- [ ] Mobile: 360x640 (Android)

**Steps for Each Viewport**:
1. Resize browser to target size
2. Open profile modal
3. Verify:
   - Modal fits on screen
   - All fields are visible
   - Buttons are clickable/tappable
   - No horizontal scrolling needed
4. Test form interactions

**Expected Results**:
- [ ] Modal is responsive and fits all viewports
- [ ] Form fields remain accessible on mobile
- [ ] Avatar preview is properly sized
- [ ] No layout overflow or distortion
- [ ] Modal is centered properly on all screen sizes

**Notes**:
- Use DevTools (F12) → Device Toolbar to test responsive design
- Test both portrait and landscape orientations on mobile

---

### Test 15: Network & Error Scenarios
**Objective**: Verify graceful handling of network issues

**Scenarios**:

**Scenario A: Slow Network**:
1. Open DevTools → Network tab
2. Throttle to "Slow 3G"
3. Try to save profile changes
4. Observe loading behavior

**Expected Results**:
- [ ] Toast notification appears after data loads
- [ ] Modal doesn't hang or freeze
- [ ] Operation completes eventually

**Scenario B: Supabase Unreachable**:
1. Open DevTools → Network tab
2. Filter requests to Supabase domain
3. Block Supabase requests (or disconnect internet briefly)
4. Try to save profile changes

**Expected Results**:
- [ ] Error is handled gracefully
- [ ] User sees appropriate error message
- [ ] No infinite loading state
- [ ] Modal remains functional

**Scenario C: Missing user_profiles Table**:
1. Open browser console
2. Try to save profile changes with missing table
3. Check console for error messages

**Expected Results**:
- [ ] Code detects PGRST116 error (table not found)
- [ ] User sees success message (name updated in local state)
- [ ] Console shows: "Note: user_profiles table not available, saving to local state only"
- [ ] Changes persist during current session

**Notes**:
- These are edge cases; the table should exist in production
- Verify graceful degradation when Supabase is unavailable

---

## Test Execution Checklist

### Critical Tests (Must Pass):
- [ ] Profile modal opens correctly
- [ ] User data loads correctly from Supabase
- [ ] Name can be edited and saved
- [ ] Modal closes properly (all methods)
- [ ] Read-only fields cannot be modified
- [ ] Validation prevents saving empty names
- [ ] Changes persist after page reload

### Important Tests (Should Pass):
- [ ] Avatar image preview works with file upload
- [ ] Toast notifications display with correct styling
- [ ] Both admin and viewer roles work correctly
- [ ] Supabase integration saves data correctly
- [ ] Error messages display for validation failures

### Nice-to-Have Tests (Should Pass):
- [ ] Works across multiple browsers
- [ ] Responsive on mobile devices
- [ ] Handles concurrent user sessions correctly
- [ ] Graceful error handling for network issues

---

## Troubleshooting Guide

### Modal doesn't open
- [ ] Check browser console (F12) for JavaScript errors
- [ ] Verify Supabase authentication is successful
- [ ] Try refreshing the page
- [ ] Clear browser cache and reload

### Data doesn't load or save
- [ ] Verify Supabase connection in browser console
- [ ] Check Supabase project settings (is it active?)
- [ ] Verify `user_roles` table has test user data
- [ ] Verify `user_profiles` table exists or can be created
- [ ] Check browser network requests (DevTools → Network tab)

### Avatar doesn't display
- [ ] Check file input is working (can you select a file?)
- [ ] Verify selected file is a valid image (JPEG, PNG, GIF, WebP)
- [ ] Check browser console for FileReader errors
- [ ] Try with a different image file

### Styling looks wrong
- [ ] Check CSS is properly loaded (DevTools → Elements)
- [ ] Verify colors are correct (#4F46E5 for admin, #10B981 for viewer)
- [ ] Clear browser cache and reload
- [ ] Try in a different browser

### Toast notifications don't appear
- [ ] Check browser console for visibility issues
- [ ] Verify CSS for .toast element is loaded
- [ ] Check that success/error classes are applied
- [ ] Try a different browser

---

## Test Results Documentation

Use the table below to document your test results:

| Test #  | Test Name | Status | Notes | Date |
|---------|-----------|--------|-------|------|
| 1 | Authentication & Avatar Display | PASS/FAIL | | |
| 2 | Avatar Dropdown Menu | PASS/FAIL | | |
| 3 | Opening Profile Modal | PASS/FAIL | | |
| 4 | Profile Data Population | PASS/FAIL | | |
| 5 | Avatar Image Preview | PASS/FAIL | | |
| 6 | Read-Only Fields Validation | PASS/FAIL | | |
| 7 | Name Field Editing | PASS/FAIL | | |
| 8 | Save Profile Changes - Success | PASS/FAIL | | |
| 9 | Save Profile Changes - Validation Error | PASS/FAIL | | |
| 10 | Closing Profile Modal | PASS/FAIL | | |
| 11 | Admin vs Viewer Behavior | PASS/FAIL | | |
| 12 | Concurrent User Sessions | PASS/FAIL | | |
| 13 | Cross-Browser Testing | PASS/FAIL | | |
| 14 | Responsive Design Testing | PASS/FAIL | | |
| 15 | Network & Error Scenarios | PASS/FAIL | | |

---

## Sign-Off

**Tester Name**: ___________________
**Date**: ___________________
**Overall Status**: [ ] PASS [ ] FAIL
**Notes**: ___________________

---

**Generated**: 2026-05-14
**HTTP Server**: http://localhost:8000
**Application File**: ML63.html
**Test Plan**: See PROFILE_MODAL_TEST_PLAN.md
**Logic Tests**: 26/26 Passed ✅
