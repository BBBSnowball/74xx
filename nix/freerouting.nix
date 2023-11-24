{ stdenv, fetchurl, bash, openjdk }:

stdenv.mkDerivation rec {
  pname = "freerouting";
  version = "1.9.0";

  src = fetchurl {
    url = "https://github.com/freerouting/freerouting/releases/download/v${version}/freerouting-${version}.jar";
    hash = "sha256-kISkiIk3p/MfhX7MEqp6N0B/URYOTSiS3/nJu0euMQI=";
  };

  phases = [ "installPhase" ];

  start = ''
    #! ${bash}/bin/bash
    if [ -n "$WAYLAND_DISPLAY" ] ; then
      export _JAVA_AWT_WM_NONREPARENTING=1
    fi
    exec ${openjdk}/bin/java -jar @out@/share/freerouting/freerouting.jar "$@"
  '';
  passAsFile = [ "start" ];

  installPhase = ''
    mkdir -p $out/{bin,share/freerouting}
    cp $src $out/share/freerouting/freerouting.jar
    substitute $startPath $out/bin/freerouting --subst-var out
    chmod +x $out/bin/freerouting
  '';
}
