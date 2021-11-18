# CSS Changes

CSS in Grantnav comes from the 360 Design system:

* https://cdn.threesixtygiving.org/
* https://github.com/ThreeSixtyGiving/360-ds

Any changes to CSS must be made there first. Then the GrantNav CSS must be updated from there.

## Making changes to the Design system.

Make a pull request on https://github.com/ThreeSixtyGiving/360-ds as standard. Merge to default branch (currently master).

## Update GrantNav from Design System

Create a new branch in your local copy of the GrantNav repository.

The 360-ds repository is included as a git submodule in the directory `360-ds`. Update this to the latest version of the default branch.

If you haven't before, you may need to initialise submodules:

    git submodule init
    git submodule update

Then update:

    cd 360-ds
    git checkout master
    git pull

You then need to build the new CSS from these design system source files.

You will need node installed (See https://github.com/ThreeSixtyGiving/360-ds/blob/master/package.json engines/node key to see which version - currently 12)

In the `360-ds` directory, run:

    npm run compile-sass -- --project 'grantnav' --path '../grantnav/frontend/static/css/'

(This command is taken from https://github.com/ThreeSixtyGiving/360-ds/blob/master/README.md and there are more notes there)

Test your changes work.

Commit both these things (the changes to the submodule and main.css) in the same commit. Push your branch to GitHub and make a pull request as standard.

## Example commits

Here are some example commits that have done this before:

* https://github.com/ThreeSixtyGiving/grantnav/commit/3cc2f67f67a53dbabb2d782628b4994f704f1047
* https://github.com/ThreeSixtyGiving/grantnav/commit/e4e3faaa6d167ba426d77620002ed1c0758d3aed

