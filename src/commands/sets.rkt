#lang racket/base


(require racket/cmdline)


(define (do-sets argv)
  (command-line
      #:program "patchiman-sets"
      #:argv argv
      #:usage-help "Lists available patchsets"
      #:args ()
      0))


(provide do-sets)
