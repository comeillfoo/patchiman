#lang racket/base


(require racket/cmdline)


(define (do-reset argv)
  (command-line
    #:program "patchiman-reset"
    #:argv argv
    #:usage-help "Resets state of the project"
    #:args ()
    0))


(provide do-reset)
