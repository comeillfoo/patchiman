#lang info
(define collection "patchiman")
(define deps '("base"))
(define build-deps '("scribble-lib" "racket-doc" "rackunit-lib"))
(define scribblings '(("scribblings/patchiman.scrbl" ())))
(define pkg-desc "Patches manager for user-defined domain.")
(define version "0.0")
(define pkg-authors '(comeillfoo))
(define license '(MIT))
