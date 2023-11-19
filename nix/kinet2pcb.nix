{ buildPythonPackage, fetchFromGitHub, pytest, pytest-runner, kinparse, callPackage, hierplace ? callPackage ./hierplace.nix {} }:

buildPythonPackage rec {
  pname = "kinet2pcb";
  version = "1.1.1";
  format = "setuptools";

  src = fetchFromGitHub {
    owner = "devbisme";
    repo = pname;
    rev = version;
    hash = "sha256-2GkBz2bsAoYkSp3Iv2DCNGzP88zv9GQQstOIjNEVxtg=";
  };

  buildInputs = [ pytest pytest-runner ];

  propagatedBuildInputs = [
    kinparse
    hierplace
  ];

  # avoid error in unittest loader: "TypeError: expected str, bytes or os.PathLike object, not NoneType"
  doCheck = false;
}
