    def left_join_on_column(left, right):
        return left.merge(right, on="column", how="left")
    
