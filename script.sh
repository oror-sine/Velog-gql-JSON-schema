git clone --filter=blob:none --no-checkout https://github.com/velopert/velog-client
cd  velog-client
git sparse-checkout set src/lib/graphql/
git checkout
cd ../

python main.py

rm -rf velog-client

git add schemas
if [[ $(git diff --staged --name-only) ]]; then
    git config user.name "oror-sine"
    git config user.email "oror-sine@users.noreply.github.com"
    git commit -m "update velog-gql-json-schema"
    git push
fi