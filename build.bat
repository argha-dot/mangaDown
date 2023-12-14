@echo off

REM Run Cargo
cargo build --release

REM Check if successful
if %errorlevel% neq 0 ( 
    echo Build Failed. Exiting.
    exit /b %errorlevel%
)

REM Define the source and destination paths
set "source_path=.\target\release\manga-down.exe"
@REM dir ".\target"
set "destination_path=E:\Media\Manga"

REM Create the destination directory if it doesn't exist
if not exist "%destination_path%" mkdir "%destination_path%"

REM Move the binary to the destination
copy /Y "%source_path%" "%destination_path%"

echo Build completed successfully.