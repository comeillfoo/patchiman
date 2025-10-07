#lang racket/base


(require racket/cmdline)


(define (do-diff argv)
  (command-line
    #:program "patchiman-diff"
    #:argv argv
    #:usage-help "Prints diff"
    #:args ()
    0))


(provide do-diff)
