#lang racket/base


(require racket/cmdline racket/contract "../backends/gnu.rkt" "../backends/git.rkt")


(define/contract init-backend
  (parameter/c (or/c "gnu" "git"))
  (make-parameter "gnu"))


(define (do-init argv)
  (command-line
    #:program "patchiman-init"
    #:argv argv
    #:usage-help "Setups current folder as a project that requires patches"
    #:once-each
    [("-b" "--backend") backend
                        "Backend name to use during managing: gnu or git"
                        (init-backend backend)]
    #:args (rules)
    (make-directory ".patchiman")
    (case (init-backend)
      [("gnu") (gnu-clone)]
      [("git") (git-clone)])))


(provide do-init)
