# Makefile for Swift project automation
# Provides common tasks: build, test, format, lint, clean, and ci (continuous integration)
# Format and lint attempt to run `swift format` if available, else print a message
# Uses POSIX sh compatible shell detection and commands, no zsh dependencies

SHELL := /bin/sh

.PHONY: build test format lint clean ci

build:
	@swift build

test:
	@swift test

format:
	@if command -v swift-format >/dev/null 2>&1; then \
		echo "Running swift-format..."; \
		swift-format -i Sources Tests; \
	elif command -v swift >/dev/null 2>&1 && swift --version >/dev/null 2>&1 && swift format --help >/dev/null 2>&1; then \
		echo "Running swift format..."; \
		swift format -i Sources Tests; \
	else \
		echo "swift-format or 'swift format' command not found. Please install swift-format or use Swift 5.5+ with 'swift format'."; \
	fi

lint: format

clean:
	@swift package clean

ci: build test lint
