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

      devShells.default = pkgs.mkShell rec {
        buildInputs = (with pkgs; [
          ghdl yosys
          gnumake
          (python3.withPackages (p: with p; [
            skidl
            # disable kinet2pcb because we need our vendored version with fixes
            #(p.callPackage ./nix/kinet2pcb.nix { hierplace = p.callPackage ./nix/hierplace.nix {}; })
            kicad
          ]))
          kicad
        ]) ++ (with packages; [
          vpr
        ]);

        KICAD7_SYMBOL_DIR =  "${pkgs.kicad.libraries.footprints}/share/kicad/symbols";
        KICAD7_FOOTPRINT_DIR = "${pkgs.kicad.libraries.footprints}/share/kicad/footprints";
        KICAD_SYMBOL_DIR = KICAD7_SYMBOL_DIR;
        KICAD_FOOTPRINT_DIR = KICAD7_FOOTPRINT_DIR;
      };
    });
}
