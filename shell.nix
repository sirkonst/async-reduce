with import <nixpkgs> { };

let
  pythonPackages = python311Packages;
  pythonVenvDir = ".local/${pythonPackages.python.name}";
  envPackages = [
    gitMinimal
  ];
  preInstallPypiPackages = [
    "blue"
    "mypy"
    "pylama"
    "tox"
    "ipykernel"
  ];
in mkShell {
  name = "pythonProjectDevEnv";
  venvDir = pythonVenvDir;

  buildInputs = with pythonPackages; [
    python
    venvShellHook
  ] ++ envPackages;

  postVenvCreation = let
    toPypiInstall = lib.concatStringsSep " " preInstallPypiPackages;
  in ''
    unset SOURCE_DATE_EPOCH  # allow pip to install wheels
    PIP_DISABLE_PIP_VERSION_CHECK=1 pip install ${toPypiInstall}
  '';

  postShellHook = ''
    # fix for cython and ipython
    export LD_LIBRARY_PATH=${lib.makeLibraryPath [stdenv.cc.cc]}

    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH

    export PIP_DISABLE_PIP_VERSION_CHECK=1

    # upgrade venv if python package was updated
    python -m venv --upgrade ${pythonVenvDir}
  '';
}
