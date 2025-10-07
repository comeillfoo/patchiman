#lang racket/base


(require racket/cmdline)


(define (do-apply argv)
  (command-line
    #:program "patchiman-apply"
    #:argv argv
    #:usage-help "Applies patches"
    #:args patches
    0))


(provide do-apply)
