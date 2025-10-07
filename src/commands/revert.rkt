#lang racket/base


(require racket/cmdline)


(define (do-revert argv)
  (command-line
    #:program "patchiman-revert"
    #:argv argv
    #:usage-help "Reverts patches"
    #:args patches
    0))


(provide do-revert)
