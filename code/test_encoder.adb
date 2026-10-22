--  Exhaustive enumeration driver for Experiment 4:
--  every valid (chart, rank) pair maps to a unique address covering [0, 1024),
--  and every address decodes back to the same pair (Tier 1 correctness).

with Chart_Encoder; use Chart_Encoder;

procedure Test_Encoder is
   Seen : array (Address) of Boolean := (others => False);

   type Pair is record
      K : Chart_Id;
      R : Valid_Rank;
   end record;

   --  Store the decoding of each address to verify the round trip.
   Inverse : array (Address) of Pair;

   Count : Natural := 0;
begin
   for K in Chart_Id loop
      for R in Valid_Rank range Valid_Rank'First ..
               Valid_Rank'Val (Cells (K) - 1)
      loop
         declare
            A : constant Address := Encode (K, R);
         begin
            pragma Assert (not Seen (A));   --  injectivity on the fly
            Seen (A) := True;
            Inverse (A) := (K, R);
            Count := Count + 1;
         end;
      end loop;
   end loop;

   pragma Assert (Count = Arena_Size);
   pragma Assert (for all A in Address => Seen (A));

   --  Round trip (Tier 1).
   for A in Address loop
      declare
         K : Chart_Id;
         R : Valid_Rank;
      begin
         Decode (A, K, R);
         pragma Assert (Encode (K, R) = A);
         pragma Assert (Inverse (A).K = K and then Inverse (A).R = R);
      end;
   end loop;
end Test_Encoder;
