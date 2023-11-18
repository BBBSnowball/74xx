{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs, ... } @ inputs:
    flake-utils.lib.eachSystem [ "x86_64-linux" ] (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in rec {
      packages = flake-utils.lib.flattenTree {
        vpr = import ./kicad/vpr/vpr.nix { inherit pkgs; };
      };

      #defaultPackage = packages.hello;

      devShells.default = pkgs.mkShell {
        buildInputs = (with pkgs; [
          ghdl yosys
          gnumake
          (python3.withPackages (p: [ p.skidl ]))
          kicad
        ]) ++ (with packages; [
          vpr
        ]);
      };
    });
}
