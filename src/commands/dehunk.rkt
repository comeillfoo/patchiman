#lang racket/base


(require racket/cmdline)


(define (do-dehunk argv)
  (command-line
    #:program "patchiman-dehunk"
    #:argv argv
    #:usage-help "Eliminates minor hunks discrepancies to patches"
    #:args patches
    0))


(provide do-dehunk)
