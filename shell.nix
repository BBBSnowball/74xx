{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
	buildInputs = with pkgs; [
		ghdl yosys
		gnumake
		(python3.withPackages (p: [ p.skidl ]))
	];
}