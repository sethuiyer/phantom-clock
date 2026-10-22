with General_Chart_Encoder; use General_Chart_Encoder;

package body General_Chart_Encoder with SPARK_Mode is

   --  Induction over adjacent charts.  Is_Consistent only gives the pairwise
   --  identity Base(J) + Cells(J) = Base(J+1); the solvers will not chain it
   --  across an arbitrary gap K1 < K2, so we walk the chain.
   procedure Lemma_Monotone (T : Chart_Table; K1, K2 : Chart_Id) is
   begin
      --  Goal is Base(K1) + Cells(K1) <= Base(K2), i.e. Base(K1+1) <= Base(K2).
      --  Walk J from K1+1 to K2 keeping Base(K1+1) <= Base(J).
      --  K1 < K2 <= K_Max, so K1+1 is in Chart_Id and J <= K_Max throughout.
      for J in K1 + 1 .. K2 loop
         pragma Loop_Invariant (T.Base (K1 + 1) <= T.Base (J));
         pragma Loop_Invariant (J <= T.K_Max);
         if J < K2 then
            --  step: Base(J) < Base(J+1) because Cells(J) > 0
            pragma Assert (J < T.K_Max);
            pragma Assert (T.Base (J) + T.Cells (J) = T.Base (J + 1));
            pragma Assert (T.Cells (J) > 0);
            pragma Assert (T.Base (J) < T.Base (J + 1));
         end if;
      end loop;
      --  At exit J = K2, so Base(K1+1) <= Base(K2) and Base(K1+1) = Base(K1)+Cells(K1).
      pragma Assert (T.Base (K1) + T.Cells (K1) = T.Base (K1 + 1));
   end Lemma_Monotone;

   function Encode (T : Chart_Table; K : Chart_Id; R : Arena_Bound) return Address is
   begin
      pragma Assert (T.Base (K) + R < T.Base (K) + T.Cells (K));
      pragma Assert (T.Base (K) + T.Cells (K) <= T.Arena_Size);
      pragma Assert (T.Base (K) + R < T.Arena_Size);
      return Address (T.Base (K) + R);
   end Encode;

   procedure Lemma_Injective
     (T  : Chart_Table;
      K1 : Chart_Id;    R1 : Arena_Bound;
      K2 : Chart_Id;    R2 : Arena_Bound)
   is
   begin
      if K1 < K2 then
         Lemma_Monotone (T, K1, K2);
         --  Base(K1)+R1 < Base(K1)+Cells(K1) <= Base(K2) <= Base(K2)+R2,
         --  contradicting the precondition's equality.  Unreachable branch.
         pragma Assert (T.Base (K1) + R1 < T.Base (K1) + T.Cells (K1));
         pragma Assert (T.Base (K2) <= T.Base (K2) + R2);
         pragma Assert (T.Base (K1) + R1 < T.Base (K2) + R2);
      elsif K2 < K1 then
         Lemma_Injective (T, K2, R2, K1, R1);
      end if;
   end Lemma_Injective;

   procedure Decode
     (T : Chart_Table; A : Address; K : out Chart_Id; R : out Arena_Bound)
   is
      N : constant Arena_Bound := Arena_Bound (A);
   begin
      K := 0;
      --  Base(0) = 0 and the intervals tile [0, Arena_Size), so scanning
      --  upward while N is at or beyond the end of the current interval
      --  lands on the unique interval containing N.
      while K < T.K_Max
        and then N >= T.Base (K) + T.Cells (K)
      loop
         pragma Loop_Invariant (K < T.K_Max);
         pragma Loop_Invariant (T.Base (K) <= N);
         pragma Loop_Variant (Increases => K);
         --  Base(K+1) = Base(K) + Cells(K) <= N, so the invariant survives.
         pragma Assert (T.Base (K) + T.Cells (K) = T.Base (K + 1));
         K := K + 1;
      end loop;

      pragma Assert (T.Base (K) <= N);
      --  Either K = K_Max, and then Base(K)+Cells(K) = Arena_Size > N,
      --  or K < K_Max and the loop stopped because N < Base(K)+Cells(K).
      pragma Assert (N < T.Base (K) + T.Cells (K));

      R := N - T.Base (K);
      pragma Assert (Encode (T, K, R) = A);
   end Decode;

end General_Chart_Encoder;
