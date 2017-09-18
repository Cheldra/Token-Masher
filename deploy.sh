SOURCE_BRANCH="master"
TARGET_BRANCH="files"

git clone $REPO out
cd out
git checkout $TARGET_BRANCH || git checkout --orphan $TARGET_BRANCH
cd ..

python main.py
