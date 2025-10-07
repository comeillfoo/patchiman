#lang racket/base


(require racket/cmdline)


(define (do-branch argv)
  (command-line
    #:program "patchiman-branch"
    #:argv argv
    #:usage-help "Derives a new patchset"
    #:args (name)
    0))


(provide do-branch)
