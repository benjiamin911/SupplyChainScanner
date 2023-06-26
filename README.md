## Theory

Dependency fusion: Dependency conflicts occur when the public package manager downloads the dependent library instead of the intended dependency library/internal package manager, because a malicious attacker can download a maliciously spoofed cargo from a public repository controlled by him. Or the dependency management mechanism when using multiple software libraries. For example, when using Python's pip package manager, pip will first find the installed partition in the local environment. If it does not find the base, it will look for the public Python warehouse PyPI. By uploading a malicious stack with the same name as the public Python repository but with a higher version number to a tree's software repository, the attacker can abduct pip to download the tree's repository instead of downloading from the public Python repository.


## Prerequisite

PyPI: Need a company gitlab url & GITLAB_ACCESS_TOKEN

NPM: Need a company gitlab url & GITLAB_ACCESS_TOKEN

RubyGems: Need company rubygems address, for example http://rubygems.xxx.org/

## How to use

```
pip3 install -r ./requirements.txt 

```


### PyPI

```
python3 ./crawlPyPI.py -t 'TOKEN' -u 'GITLAB' > ./resultPyPI.txt

cat ./resultPyPI.txt | grep 'PyPI'
```

### NPM

```
python3 ./crawlNPM.py -t 'TOKEN' -u 'GITLAB' > ./resultNPM.txt

cat ./resultNPM.txt | grep 'NPM'

```

### Gem

```
python3 ./crawlGems.py -u 'INTERNAL GEM' > ./resultGems.txt

cat ./resultGems.txt | grep 'does not'

```
