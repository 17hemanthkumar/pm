@echo off
echo ========================================
echo PicMe Reviews System Setup
echo ========================================
echo.

cd backend

echo Running database setup...
python setup_reviews_system.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start your Flask server: python app.py
echo 2. Visit http://127.0.0.1:5000/homepage
echo 3. Try writing a review!
echo.
echo See REVIEWS_SYSTEM_SETUP.md for full documentation
echo.
pause
