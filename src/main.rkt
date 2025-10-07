#lang racket/base

(module+ test
  (require rackunit))

;; Notice
;; To install (from within the package directory):
;;   $ raco pkg install
;; To install (once uploaded to pkgs.racket-lang.org):
;;   $ raco pkg install <<name>>
;; To uninstall:
;;   $ raco pkg remove <<name>>
;; To view documentation:
;;   $ raco docs <<name>>
;;
;; For your convenience, we have included LICENSE-MIT and LICENSE-APACHE files.
;; If you would prefer to use a different license, replace those files with the
;; desired license.
;;
;; Some users like to add a `private/` directory, place auxiliary files there,
;; and require them in `main.rkt`.
;;
;; See the current version of the racket style guide here:
;; http://docs.racket-lang.org/style/index.html

;; Code here
(define EINVAL 22)


(module+ main
  (require racket/cmdline racket/match "commands/init.rkt" "commands/branch.rkt"
    "commands/apply.rkt" "commands/dehunk.rkt" "commands/revert.rkt"
    "commands/reset.rkt" "commands/diff.rkt" "commands/sets.rkt")

  (define (do-help argv)
    (displayln "usage: patchiman command ...")
    EINVAL)
  (define args-parse
    (command-line
      #:program "patchiman"
      #:args (cmd . rest)
      (exit
        (match cmd
          ["init" (do-init rest)]
          ["branch" (do-branch rest)]
          ["sets" (do-sets rest)]
          ["apply" (do-apply rest)]
          ["dehunk" (do-dehunk rest)]
          ["revert" (do-revert rest)]
          ["reset" (do-reset rest)]
          ["diff" (do-diff rest)]
          ["help" (do-help rest)]
          [_ (printf "unknown command: ~s\n" cmd)
             (do-help rest)])))))


(module+ test
  ;; Any code in this `test` submodule runs when this file is run using DrRacket
  ;; or with `raco test`. The code here does not run when this file is
  ;; required by another module.

  (check-equal? (+ 2 2) 4))

(module+ main
  ;; (Optional) main submodule. Put code here if you need it to be executed when
  ;; this file is run using DrRacket or the `racket` executable.  The code here
  ;; does not run when this file is required by another module. Documentation:
  ;; http://docs.racket-lang.org/guide/Module_Syntax.html#%28part._main-and-test%29
  (args-parse))
