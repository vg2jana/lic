#rm -f db.sqlite3
find . -name "__pycache__" | xargs rm -rf
rm -rf lic/migrations/
