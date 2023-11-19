{ buildPythonPackage, fetchFromGitHub }:

buildPythonPackage rec {
  pname = "HierPlace";
  version = "1.0.0";
  format = "setuptools";

  src = fetchFromGitHub {
    owner = "devbisme";
    repo = pname;
    rev = version;
    hash = "sha256-egni18T4UbqkSjsBG39oxmA5NJbDmw8IKAV/H1TEVUo=";
  };

  # avoid error in unittest loader: "TypeError: expected str, bytes or os.PathLike object, not NoneType"
  doCheck = false;
}
