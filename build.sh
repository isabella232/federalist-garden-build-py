#!/bin/bash

# TODO cancel build task if it exceeds timeout

# Stop script on errors
set -e
set -o pipefail
shopt -s extglob dotglob

# Remove sensitive environment variables
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset GITHUB_TOKEN
unset STATUS_CALLBACK
unset LOG_CALLBACK
unset FEDERALIST_BUILDER_CALLBACK

# Run build process based on configuration files

# Initialize nvm
echo "[build.sh] Initializing NVM"
. $NVM_DIR/nvm.sh

# use .nvmrc if it exists
if [[ -f .nvmrc ]]; then
  echo "[build.sh] Using node version specified in .nvmrc"
  nvm install
  nvm use
fi
echo "[build.sh] Node version: $(node -v)"
echo "[build.sh] NPM version: $(npm -v)"

# install from package.json if it exists
# run the federalist command
if [[ -f package.json ]]; then
  echo "[build.sh] Installing dependencies in package.json"
  npm install --production

  # Only run the federalist script if it is present
  FEDERALIST_SCRIPT=$(node -e "require('./package.json').scripts.federalist ? console.log('federalist') : null")
  if [[ $FEDERALIST_SCRIPT = "federalist" ]]; then
    echo "[build.sh] Running federalist build script in package.json"
    npm run federalist
  fi;
fi

echo "[build.sh] Using build engine: $GENERATOR"

# Jekyll with Gemfile plugins
if [ "$GENERATOR" = "jekyll" ]; then

  # Add Federalist configuration settings
  echo -e "\nbaseurl: ${BASEURL-"''"}\nbranch: ${BRANCH}\n${CONFIG}" >> _config.yml

  if [[ -f Gemfile ]]; then
    echo "[build.sh] Installing dependencies in Gemfile"
    bundle install
    echo "[build.sh] Building using Jekyll version: $(bundle exec jekyll -v)"
    bundle exec jekyll build --destination ./_site
  else
    echo "[build.sh] Building using Jekyll version: $(bundle exec jekyll -v)"
    jekyll build --destination ./_site
  fi

# Hugo
elif [ "$GENERATOR" = "hugo" ]; then
  echo "Hugo not installed!"
  # hugo -b ${BASEURL-"''"} -s . -d ./_site

# Static files
else
  mkdir _site
  mv !(_site) _site
fi
