{ pkgs ? import <nixpkgs> {} }:
with pkgs;

let
  python_packages = p: with p; [
    pip
    virtualenv
    lxml
    python-utils
  ];
  python3 = pkgs.python3.withPackages python_packages;
in
stdenv.mkDerivation rec {
  name = "vtr-${version}";
  version = "local";

  src = fetchFromGitHub {
    owner = "verilog-to-routing";
    repo = "vtr-verilog-to-routing";
    rev = "e97bb0b45ab387e3945e11e3d3b69b74a6f06eae";  # master, 2023-11-16
    fetchSubmodules = true;
    hash = "sha256-8WukqMZnqSQZ7HoLjAyI6OtU1JpW9Acxyil8yk5XLt8=";
  };

  buildInputs = [
    #NOTE libtatum would like to use tbb (Intel Thread Building Blocks C++ Library) but its cmake file doesn't find it.
    #     We don't care, for now, because that only means that STA won't run in parallel and we aren't going to use STA.
    #     -> Actually, we have the same issue for vpr.
    #     -> Fixed by adding a custom TBBConfig.cmake file.
    tbb
    xorg.libX11
    xorg.libXft
    cairo
    gtk3
    eigen

    # dependencies of glib and gio
    xorg.libxcb
    xorg.libXdmcp
    pcre2
    libuuid  # mount.pc
    libselinux
    libsepol
    pcre
  ];

  nativeBuildInputs = with pkgs; [
    bison
    flex
    cmake
    fontconfig
    pkgconfig
    clang
    clang-tools
    gperftools
    perl
    python3
    time
    tcl
    #wget
    (pkgs.writeScriptBin "wget" ''
      echo "DEBUG: wget $*" >&2
      if [ "$1" == "https://raw.githubusercontent.com/capnproto/capnproto-java/master/compiler/src/main/schema/capnp/java.capnp" -a "$2" == "-O" -a -n "$3" ] ; then
        cp ${java_capnp} "$3"
      else
        echo "ERROR: Unsupported arguments for fake wget!" >&2
        exit 1
      fi
    '')
  ];

  #cmakeFlags = [
  #  "-DTBB_INCLUDE_DIR=.../include"
  #  "-DENABLE_LTO=True"
  #];

  # Point cmake to our TBBConfig.cmake file.
  TBB_DIR = builtins.dirOf ./TBBConfig.cmake;

  java_capnp = fetchurl {
    url = "https://raw.githubusercontent.com/capnproto/capnproto-java/ed9a67c5fcd46604a88593625a9e38496b83d3ab/compiler/src/main/schema/capnp/java.capnp";
    hash = "sha256-q8SNhZ/6Bqwmx9/mAgN0+w7l76STZwerw1vawiM676s=";
  };

  #postPatch = ''
  #  # cmake will run the custom command anyway (because it actually wants the file in the build dir) so we have a fake wget (see above).
  #  # Actual target location is: /build/source/build/libs/libvtrcapnproto/schema/capnp/java.capnp
  #  mkdir -p libs/libvtrcapnproto/schema/capnp
  #  cp $java_capnp libs/libvtrcapnproto/schema/capnp/java.capnp
  #'';

  # method 1: skip Nix' hooks for cmake and let vtr's Makefile do the job

  dontConfigure = true;

  buildPhase = ''
    #make MAKECMDGOALS=vpr
    make vpr -j$NIX_BUILD_CORES
  '';

  # method 2: tell Nix about the args that would be added by vtr's Makefile
  # -> doesn't work because we somehow call the inner Makefile2 with "all"

  #cmakeFlags = [
  #  #"-DCMAKE_BUILD_TYPE=release"
  #  #"-G" "Unix Makefiles"
  #];
  #makeFlags = [
  #  # build only vpr because we don't need the others and yosys build would fail:
  #  # see https://github.com/YosysHQ/yosys/issues/681
  #  # and https://github.com/NixOS/nixpkgs/blob/nixos-23.05/pkgs/development/compilers/yosys/fix-clang-build.patch
  #  "vpr"
  #];
}
