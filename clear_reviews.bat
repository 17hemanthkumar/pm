@echo off
echo ========================================
echo Clear All Reviews - PicMe
echo ========================================
echo.
echo WARNING: This will delete ALL reviews from the database!
echo.

cd backend
python clear_all_reviews.py

echo.
pause
